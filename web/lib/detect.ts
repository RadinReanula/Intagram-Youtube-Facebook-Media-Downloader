import type { Platform } from "@/lib/types";

const YOUTUBE_ID = /^[A-Za-z0-9_-]{6,}$/;

export type Detection = {
  platform: Platform;
  mediaType: string | null;
};

export function detectLink(raw: string): Detection | null {
  const text = raw.trim();
  if (!text) return null;
  let url: URL;
  try {
    url = new URL(text);
  } catch {
    return null;
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") return null;
  const host = url.hostname.toLowerCase();
  const parts = url.pathname.split("/").filter(Boolean);
  const head = (parts[0] || "").toLowerCase();

  if (host === "youtu.be" || host.endsWith(".youtu.be") || host === "youtube.com" || host.endsWith(".youtube.com")) {
    if (head === "shorts" && parts[1] && YOUTUBE_ID.test(parts[1])) return { platform: "youtube", mediaType: "short" };
    if (head === "watch" || host.endsWith("youtu.be")) return { platform: "youtube", mediaType: "video" };
    if (head === "playlist" || head === "channel" || head.startsWith("@")) return { platform: "youtube", mediaType: null };
    return { platform: "youtube", mediaType: "video" };
  }
  if (host === "instagram.com" || host.endsWith(".instagram.com") || host === "instagr.am" || host.endsWith(".instagr.am")) {
    if (head === "reel" || head === "reels") return { platform: "instagram", mediaType: "reel" };
    if (head === "p") return { platform: "instagram", mediaType: "post" };
    if (head === "stories") return { platform: "instagram", mediaType: "story" };
    if (head === "tv") return { platform: "instagram", mediaType: "video" };
    return { platform: "instagram", mediaType: null };
  }
  if (
    host === "facebook.com" ||
    host.endsWith(".facebook.com") ||
    host === "fb.com" ||
    host.endsWith(".fb.com") ||
    host === "fb.watch" ||
    host.endsWith(".fb.watch")
  ) {
    const lowered = parts.map((part) => part.toLowerCase());
    if (lowered[0] === "share" && lowered[1]) {
      if (lowered[1] === "r") return { platform: "facebook", mediaType: "reel" };
      if (lowered[1] === "p") return { platform: "facebook", mediaType: "post" };
      return { platform: "facebook", mediaType: "video" };
    }
    if (lowered.includes("reel") || lowered.includes("reels")) return { platform: "facebook", mediaType: "reel" };
    if (lowered.includes("watch") || lowered.includes("videos") || host.endsWith("fb.watch")) {
      return { platform: "facebook", mediaType: "video" };
    }
    if (lowered.includes("posts") || lowered.includes("photos") || lowered.includes("photo")) {
      return { platform: "facebook", mediaType: "post" };
    }
    return { platform: "facebook", mediaType: null };
  }
  return null;
}

export function platformLabel(platform: Platform): string {
  if (platform === "youtube") return "YouTube";
  if (platform === "instagram") return "Instagram";
  return "Facebook";
}
