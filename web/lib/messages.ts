const MESSAGES: Record<string, string> = {
  invalid_link: "That doesn't look like a valid link.",
  private_content: "This content is private or needs a login, so it can't be downloaded.",
  not_found: "This content was not found. It may have been deleted.",
  unsupported: "This type of link isn't supported. Try a single public video, reel, post or story.",
  blocked: "The platform blocked the request. Try again later.",
  busy: "The server is busy. Try again later.",
  limit_exceeded: "This file is larger or longer than the allowed limit.",
};

export function messageFor(code: string | null | undefined, fallback?: string | null, position?: number | null): string {
  if (code === "busy" && position) {
    return `The server is busy. You are number ${position} in the queue.`;
  }
  if (fallback) return fallback;
  if (code && MESSAGES[code]) return MESSAGES[code];
  return "Something went wrong. Try again.";
}
