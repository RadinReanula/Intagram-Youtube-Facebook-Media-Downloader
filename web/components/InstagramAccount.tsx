"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { getSession, loginInstagram, logoutInstagram, verifyInstagram } from "@/lib/api";
import { ApiClientError } from "@/lib/types";

export function InstagramAccount() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const session = useQuery({ queryKey: ["session"], queryFn: getSession, retry: false });

  useEffect(() => {
    const openDialog = () => setOpen(true);
    window.addEventListener("ig-login-required", openDialog);
    return () => window.removeEventListener("ig-login-required", openDialog);
  }, []);

  function signedIn() {
    queryClient.invalidateQueries({ queryKey: ["session"] });
    setOpen(false);
    window.dispatchEvent(new Event("ig-signed-in"));
  }

  const logout = useMutation({
    mutationFn: logoutInstagram,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["session"] }),
  });

  const username = session.data?.signed_in ? session.data.username : null;

  return (
    <>
      {username ? (
        <button
          type="button"
          className="inline-flex min-h-11 items-center rounded-full border border-[var(--line)] bg-surface px-4 text-[0.8125rem] font-medium"
          onClick={() => logout.mutate()}
        >
          @{username}, Sign out
        </button>
      ) : (
        <button
          type="button"
          className="inline-flex min-h-11 items-center rounded-full bg-accent px-4 text-[0.8125rem] font-semibold text-on-accent"
          onClick={() => setOpen(true)}
        >
          Sign in to Instagram
        </button>
      )}
      {open ? <SignInDialog onClose={() => setOpen(false)} onSuccess={signedIn} /> : null}
    </>
  );
}

function SignInDialog({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [challenge, setChallenge] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const login = useMutation({
    mutationFn: () => loginInstagram(username.trim(), password),
    onSuccess: (result) => {
      setPassword("");
      setError(null);
      if (result.status === "two_factor" && result.challenge_id) {
        setChallenge(result.challenge_id);
        return;
      }
      onSuccess();
    },
    onError: (reason) => setError(reason instanceof ApiClientError ? reason.message : "Instagram didn't accept that sign-in."),
  });

  const verify = useMutation({
    mutationFn: () => verifyInstagram(username.trim(), challenge || "", code.trim()),
    onSuccess: () => onSuccess(),
    onError: (reason) => setError(reason instanceof ApiClientError ? reason.message : "That code was not accepted."),
  });

  return (
    <div className="fixed inset-0 z-30 grid place-items-center bg-black/40 px-4" role="presentation" onClick={onClose}>
      <form
        role="dialog"
        aria-labelledby="ig-title"
        className="w-full max-w-md rounded-[28px] border border-[var(--line)] bg-surface p-6 shadow-[var(--shadow)]"
        onClick={(event) => event.stopPropagation()}
        onSubmit={(event) => {
          event.preventDefault();
          if (challenge) verify.mutate();
          else login.mutate();
        }}
      >
        <h2 id="ig-title" className="display text-[1.75rem] leading-tight">
          {challenge ? "Enter the Instagram code" : "Sign in to Instagram"}
        </h2>
        <p className="mt-2 text-sm text-muted">
          The password is sent once to this server, used to open your Instagram session, and then dropped. It is not saved.
        </p>
        {challenge ? (
          <label className="mt-4 grid gap-1 text-sm font-medium">
            Code
            <input
              value={code}
              onChange={(event) => setCode(event.target.value)}
              inputMode="numeric"
              autoComplete="one-time-code"
              className="h-11 rounded-2xl border border-[var(--line)] bg-bg px-3 font-normal"
            />
          </label>
        ) : (
          <div className="mt-4 grid gap-3">
            <label className="grid gap-1 text-sm font-medium">
              Username
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
                className="h-11 rounded-2xl border border-[var(--line)] bg-bg px-3 font-normal"
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Password
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                className="h-11 rounded-2xl border border-[var(--line)] bg-bg px-3 font-normal"
              />
            </label>
          </div>
        )}
        {error ? <p className="mt-3 text-sm text-failed">{error}</p> : null}
        <div className="mt-5 flex gap-2">
          <button type="button" onClick={onClose} className="min-h-11 rounded-full border border-[var(--line)] px-4 text-sm">
            Cancel
          </button>
          <button type="submit" disabled={login.isPending || verify.isPending} className="press min-h-11 flex-1 rounded-full bg-accent px-4 text-sm font-semibold text-on-accent disabled:opacity-45">
            {challenge ? "Confirm code" : "Sign in with Instagram password"}
          </button>
        </div>
      </form>
    </div>
  );
}
