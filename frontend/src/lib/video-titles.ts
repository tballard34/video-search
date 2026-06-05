export function formatVideoTitle(videoNumber?: number): string {
  return videoNumber ? `Video ${videoNumber}` : "Video";
}
