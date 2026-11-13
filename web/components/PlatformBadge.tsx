import { platformLabel, type Detection } from "@/lib/detect";

export function PlatformBadge({ detection }: { detection: Detection }) {
  const label = detection.mediaType
    ? `${platformLabel(detection.platform)} ${detection.mediaType}`
    : platformLabel(detection.platform);
  return (
    <span className={`badge-${detection.platform} inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium text-white`}>
      {label}
    </span>
  );
}
