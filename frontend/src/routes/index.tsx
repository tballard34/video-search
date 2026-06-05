import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { TbPlus, TbVideo } from "react-icons/tb";

import { addLocalVideo, listLocalVideos, type LocalVideo } from "@/lib/local-videos";
import { formatVideoTitle } from "@/lib/video-titles";

export const Route = createFileRoute("/")({
  component: VideosPage,
});

function LocalVideoThumbnail({ video }: { video: LocalVideo }) {
  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-gray-900">
      <video src={video.videoUrl} className="h-full w-full object-cover" muted playsInline preload="metadata" />
    </div>
  );
}

function EmptyVideoPreview() {
  return (
    <div className="flex aspect-video w-full items-center justify-center rounded-lg bg-gray-900">
      <TbVideo className="h-12 w-12 text-gray-600" />
    </div>
  );
}

function VideosPage() {
  const navigate = useNavigate();
  const [localVideos, setLocalVideos] = useState<LocalVideo[]>(() => listLocalVideos());
  const [showUploadModal, setShowUploadModal] = useState(false);

  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setShowUploadModal(false);
    const title = formatVideoTitle(localVideos.length + 1);
    addLocalVideo(file, title);
    setLocalVideos(listLocalVideos());
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/mp4": [".mp4"],
    },
    maxSize: 500 * 1024 * 1024,
    multiple: false,
  });

  return (
    <div className="flex h-full flex-col bg-background">
      <header className="flex items-center justify-between border-b border-border bg-surface px-8 py-5">
        <h1 className="text-2xl font-bold text-foreground">Videos</h1>
        <button
          onClick={() => setShowUploadModal(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-gray-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800"
        >
          <TbPlus size={18} />
          Add
        </button>
      </header>

      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/10 backdrop-blur-sm" onClick={() => setShowUploadModal(false)}>
          <div className="mx-4 w-full max-w-2xl rounded-2xl border-2 border-gray-900 bg-white p-6 shadow-xl sm:p-16" onClick={(event) => event.stopPropagation()}>
            <div
              {...getRootProps()}
              className={`flex h-72 cursor-pointer items-center justify-center rounded-xl border-2 border-dashed transition sm:h-96 ${
                isDragActive ? "border-gray-900 bg-gray-50" : "border-gray-400 hover:border-gray-600"
              }`}
            >
              <input {...getInputProps()} />
              <div className="text-center">
                {isDragActive ? (
                  <p className="text-xl font-medium text-gray-900 sm:text-2xl">Drop your video here</p>
                ) : (
                  <p className="text-xl font-medium text-gray-900 sm:text-2xl">Add a video</p>
                )}
                <p className="mt-4 text-sm text-gray-500">Drag & drop a video file or click to browse</p>
                <p className="mt-2 text-xs text-gray-400">MP4 only • Max 500MB</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 p-5 sm:p-8">
        {localVideos.length === 0 ? (
          <div className="text-center text-foreground-secondary">No videos yet. Click the <span className="font-semibold">Add</span> button above to create your first video.</div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
            {localVideos.map((video) => (
              <div
                key={video.id}
                className="flex cursor-pointer flex-col transition-transform hover:scale-[1.02]"
                onClick={() => navigate({ to: "/videos/$videoId", params: { videoId: video.id } })}
              >
                {video.videoUrl ? <LocalVideoThumbnail video={video} /> : <EmptyVideoPreview />}

                <h3 className="mt-3 text-center font-medium text-foreground">{video.title}</h3>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
