export function ErrorNotice({ message }: { message: string }) {
  return (
    <p role="alert" className="rounded-2xl bg-[color-mix(in_srgb,var(--failed)_12%,transparent)] px-4 py-3 text-sm text-failed">
      {message}
    </p>
  );
}
