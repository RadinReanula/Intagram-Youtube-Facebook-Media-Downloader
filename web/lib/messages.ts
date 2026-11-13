const TITLES: Record<string, [string, string]> = {
  invalid_link: ["This isn’t a supported link", "Paste one public video, reel or post from YouTube, Instagram or Facebook."],
  private_content: ["This content isn’t public", "Only public posts can be saved. Sign in with your Instagram account if this is your own story."],
  not_found: ["This content was not found", "It may have been deleted. Check the link and try again."],
  unsupported: ["This type of link isn’t supported", "Try a single public video, reel, post or story."],
  blocked: ["The platform blocked the request", "Wait a moment and try the link again."],
  busy: ["The server is busy", "Nothing was started. Wait a minute and press Analyse again."],
  limit_exceeded: ["This file is over the limit", "Choose a smaller format, or try a shorter video."],
  login_required: ["Instagram needs a sign-in", "Stories and some posts are only available from your own account. Sign in to continue."],
};

export type ErrorCopy = { title: string; detail: string };

export function errorCopy(code: string | null | undefined, fallback?: string | null, position?: number | null): ErrorCopy {
  if (code === "busy" && position) {
    return { title: "The server is busy", detail: `Nothing was started. You are number ${position} in line, so try again in a minute.` };
  }
  if (code && TITLES[code]) {
    const [title, detail] = TITLES[code];
    return { title, detail: fallback && fallback !== detail ? fallback : detail };
  }
  if (fallback) return { title: "Something went wrong", detail: fallback };
  return { title: "Something went wrong", detail: "Try again." };
}

export function messageFor(code: string | null | undefined, fallback?: string | null, position?: number | null): string {
  const copy = errorCopy(code, fallback, position);
  return copy.detail;
}
