export type Platform = "youtube" | "instagram" | "facebook";

export type FormatOption = {
  id: string;
  label: string;
  ext: string;
  kind: "video" | "audio" | "image";
  filesize: number | null;
  over_limit: boolean;
  warning: string | null;
};

export type MediaItem = {
  index: number;
  title: string | null;
  thumbnail: string | null;
  duration: number | null;
  media_type: string;
  formats: FormatOption[];
};

export type AnalyzeResult = {
  platform: Platform;
  media_type: string;
  title: string | null;
  thumbnail: string | null;
  duration: number | null;
  uploader: string | null;
  items: MediaItem[];
  can_download_all: boolean;
  cached: boolean;
};

export type JobView = {
  id: string;
  status: "queued" | "processing" | "ready" | "failed" | "cancelled";
  progress: number;
  position: number | null;
  error_code: string | null;
  error_message: string | null;
  file_name: string | null;
  file_size: number | null;
  download_url: string | null;
};

export class ApiClientError extends Error {
  code: string;
  position?: number;

  constructor(code: string, message: string, position?: number) {
    super(message);
    this.code = code;
    this.position = position;
  }
}
