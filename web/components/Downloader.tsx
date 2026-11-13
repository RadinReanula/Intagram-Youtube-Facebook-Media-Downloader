"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { ErrorNotice } from "@/components/ErrorNotice";
import { FormatPicker } from "@/components/FormatPicker";
import { JobStatus } from "@/components/JobStatus";
import { PreviewCard, PreviewSkeleton } from "@/components/PreviewCard";
import { StepTracker } from "@/components/StepTracker";
import { Turnstile } from "@/components/Turnstile";
import { UrlField } from "@/components/UrlField";
import { analyze, cancelJob, createJob, getJob } from "@/lib/api";
import { errorCopy } from "@/lib/messages";
import { ApiClientError, type AnalyzeResult, type FormatOption } from "@/lib/types";

export function Downloader() {
  const queryClient = useQueryClient();
  const [url, setUrl] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [itemIndex, setItemIndex] = useState(0);
  const [formatId, setFormatId] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<ReturnType<typeof errorCopy> | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const analyse = useMutation({
    mutationFn: (next: string) => analyze(next, token),
    onSuccess: (data, next) => {
      setUrl(next);
      setResult(data);
      setItemIndex(data.items[0]?.index ?? 0);
      setFormatId(data.items[0]?.formats.find((format) => !format.over_limit)?.id ?? data.items[0]?.formats[0]?.id ?? null);
      setJobId(null);
      setError(null);
    },
    onError: (reason, next) => {
      setResult(null);
      setJobId(null);
      if (reason instanceof ApiClientError && reason.code === "login_required") {
        window.dispatchEvent(new Event("ig-login-required"));
        setUrl(next);
      }
      setError(reason instanceof ApiClientError ? errorCopy(reason.code, reason.message, reason.position) : errorCopy(null));
    },
  });

  const urlRef = useRef<string | null>(null);
  const retryRef = useRef(analyse.mutate);
  urlRef.current = url;
  retryRef.current = analyse.mutate;
  useEffect(() => {
    const retry = () => {
      if (urlRef.current) retryRef.current(urlRef.current);
    };
    window.addEventListener("ig-signed-in", retry);
    return () => window.removeEventListener("ig-signed-in", retry);
  }, []);

  const job = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId as string),
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "queued" || status === "processing" ? 1000 : false;
    },
  });

  const start = useMutation({
    mutationFn: (input: { formatId: string; itemIndex: number | null }) => {
      if (!url) throw new ApiClientError("invalid_link", "Paste a link first.");
      return createJob(url, input.formatId, input.itemIndex, token);
    },
    onMutate: () => setError(null),
    onSuccess: (created) => {
      setJobId(created.id);
      setError(null);
      queryClient.setQueryData(["job", created.id], created);
    },
    onError: (reason) => setError(reason instanceof ApiClientError ? errorCopy(reason.code, reason.message, reason.position) : errorCopy(null)),
  });

  const cancel = useMutation({
    mutationFn: () => cancelJob(jobId as string),
    onSuccess: (updated) => {
      queryClient.setQueryData(["job", updated.id], updated);
    },
  });

  const status = job.data?.status;
  const step = status === "ready" ? 4 : status === "queued" || status === "processing" ? 3 : result ? 2 : 1;

  function chooseFormat(format: FormatOption) {
    setFormatId(format.id);
    setJobId(null);
  }

  return (
    <div>
      <UrlField busy={analyse.isPending} onSubmit={(next) => analyse.mutate(next)} />
      <StepTracker current={analyse.isPending ? 2 : step} />
      <Turnstile onToken={setToken} />
      {error ? <ErrorNotice copy={error} /> : null}
      {analyse.isPending ? <PreviewSkeleton /> : null}
      <AnimatePresence mode="popLayout">
        {result && !analyse.isPending ? <PreviewCard key={`${result.platform}-${result.title}`} result={result} /> : null}
      </AnimatePresence>
      {result && !analyse.isPending ? (
        <FormatPicker
          items={result.items}
          canDownloadAll={result.can_download_all}
          itemIndex={itemIndex}
          formatId={formatId}
          starting={start.isPending}
          onItem={(index) => {
            setItemIndex(index);
            const next = result.items.find((item) => item.index === index);
            setFormatId(next?.formats.find((format) => !format.over_limit)?.id ?? next?.formats[0]?.id ?? null);
            setJobId(null);
          }}
          onFormat={chooseFormat}
          onAll={() => start.mutate({ formatId: "all", itemIndex: null })}
          onStart={() => formatId && start.mutate({ formatId, itemIndex })}
        />
      ) : null}
      {job.data ? (
        <JobStatus
          job={job.data}
          cancelling={cancel.isPending}
          onCancel={() => cancel.mutate()}
          onReset={() => {
            setResult(null);
            setJobId(null);
            setUrl(null);
            setError(null);
          }}
        />
      ) : null}
    </div>
  );
}
