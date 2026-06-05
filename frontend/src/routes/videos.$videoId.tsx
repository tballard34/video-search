import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { TbArrowLeft, TbTrash, TbVideo } from "react-icons/tb";

import { getLocalVideo, removeLocalVideo } from "@/lib/local-videos";

export const Route = createFileRoute("/videos/$videoId")({
  component: VideoDetailPage,
});

function VideoDetailPage() {
  const navigate = useNavigate();
  const { videoId } = Route.useParams();
  const video = getLocalVideo(videoId);
  const [videoLoaded, setVideoLoaded] = useState(false);

  function handleDelete() {
    removeLocalVideo(videoId);
    void navigate({ to: "/" });
  }

  if (!video) {
    return <div className="flex h-full items-center justify-center text-foreground-secondary">Video not found</div>;
  }

  return (
    <div className="flex h-full flex-col bg-background">
      <header className="flex items-center justify-between border-b border-border bg-surface px-8 py-4">
        <div className="flex min-w-0 flex-1 items-center gap-4">
          <button
            onClick={() => navigate({ to: "/" })}
            className="inline-flex flex-shrink-0 items-center gap-2 rounded-md px-2 py-1 text-sm font-medium text-foreground-secondary transition hover:bg-gray-100 hover:text-foreground"
          >
            <TbArrowLeft size={18} />
            Back
          </button>

          <h1 className="truncate text-xl font-bold text-foreground">{video.title}</h1>
        </div>

        <button
          onClick={handleDelete}
          className="inline-flex items-center gap-2 rounded-lg border border-red-200 bg-white px-4 py-2 text-sm font-semibold text-red-600 transition hover:bg-red-50"
        >
          <TbTrash size={18} />
          Delete
        </button>
      </header>

      <div className="flex min-h-0 flex-1 items-center justify-center p-8">
        <div className="w-full max-w-5xl">
          <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-gray-900 shadow-2xl shadow-gray-950/10">
            <div className="absolute inset-0 flex items-center justify-center">
              <TbVideo className="h-12 w-12 text-gray-600" />
            </div>
            <video
              src={video.videoUrl}
              controls
              className={`absolute inset-0 h-full w-full transition-opacity duration-300 ${videoLoaded ? "opacity-100" : "opacity-0"}`}
              onLoadedData={() => setVideoLoaded(true)}
            >
              Your browser does not support the video tag.
            </video>
          </div>
        </div>
      </div>
    </div>
  );
}
