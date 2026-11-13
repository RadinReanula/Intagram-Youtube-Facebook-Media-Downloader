"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence } from "motion/react";
import { useState } from "react";
import { ErrorNotice } from "@/components/ErrorNotice";
import { FormatPicker } from "@/components/FormatPicker";
import { JobStatus } from "@/components/JobStatus";
import { PreviewCard } from "@/components/PreviewCard";
import { Turnstile } from "@/components/Turnstile";
import { UrlField } from "@/components/UrlField";
import { analyze, cancelJob, createJob, getJob } from "@/lib/api";
import { ApiClientError, type AnalyzeResult, type FormatOption } from "@/lib/types";

export function Downloader() {
  const queryClient = useQueryClient();
  const [url, setUrl] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [itemIndex, setItemIndex] = useState(0);
  const [formatId, setFormatId] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const analyse = useMutation({
    mutationFn: (next: string) => analyze(next, token),
    onSuccess: (data, next) => {
      setUrl(next);
      setResult(data);
      setItemIndex(data.items[0]?.index ?? 0);
      setFormatId(data.items[0]?.formats[0]?.id ?? null);
      setJobId(null);
      setError(null);
    },
    onError: (reason) => setError(reason instanceof ApiClientError ? reason.message : "Something went wrong. Try again."),
  });

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
    onError: (reason) => setError(reason instanceof ApiClientError ? reason.message : "Something went wrong. Try again."),
  });

  const cancel = useMutation({
    mutationFn: () => cancelJob(jobId as string),
    onSuccess: (updated) => {
      queryClient.setQueryData(["job", updated.id], updated);
    },
  });

  const selected = result?.items.find((item) => item.index === itemIndex)?.formats.find((format) => format.id === formatId) ?? null;

  function chooseFormat(format: FormatOption) {
    setFormatId(format.id);
    setJobId(null);
  }

  return (
    <div className="grid gap-6">
      <UrlField busy={analyse.isPending} onSubmit={(next) => analyse.mutate(next)} />
      <Turnstile onToken={setToken} />
      {error ? <ErrorNotice message={error} /> : null}
      <AnimatePresence mode="popLayout">
        {result ? <PreviewCard key={`${result.platform}-${result.title}`} result={result} /> : null}
      </AnimatePresence>
      {result ? (
        <FormatPicker
          items={result.items}
          canDownloadAll={result.can_download_all}
          itemIndex={itemIndex}
          formatId={formatId}
          onItem={(index) => {
            setItemIndex(index);
            const next = result.items.find((item) => item.index === index);
            setFormatId(next?.formats[0]?.id ?? null);
            setJobId(null);
          }}
          onFormat={chooseFormat}
          onAll={() => start.mutate({ formatId: "all", itemIndex: null })}
        />
      ) : null}
      {result && selected ? (
        <button
          type="button"
          disabled={selected.over_limit || start.isPending || !formatId}
          onClick={() => formatId && start.mutate({ formatId, itemIndex })}
          className="press h-12 rounded-full bg-accent text-sm font-medium text-white disabled:opacity-40"
        >
          {start.isPending ? "Starting" : selected.over_limit ? "Over the limit" : "Start download"}
        </button>
      ) : null}
      {job.data ? <JobStatus job={job.data} cancelling={cancel.isPending} onCancel={() => cancel.mutate()} /> : null}
    </div>
  );
}
