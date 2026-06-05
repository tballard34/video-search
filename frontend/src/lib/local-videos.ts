export type LocalVideo = {
  id: string;
  title: string;
  videoUrl: string;
  createdAt: string;
};

const localVideos: LocalVideo[] = [];

export function addLocalVideo(file: File, title: string): LocalVideo {
  const video = {
    id: `local-${Date.now()}`,
    title,
    videoUrl: URL.createObjectURL(file),
    createdAt: new Date().toISOString(),
  };

  localVideos.unshift(video);
  return video;
}

export function getLocalVideo(id: string): LocalVideo | undefined {
  return localVideos.find((video) => video.id === id);
}

export function listLocalVideos(): LocalVideo[] {
  return [...localVideos];
}

export function removeLocalVideo(id: string): void {
  const index = localVideos.findIndex((video) => video.id === id);

  if (index === -1) {
    return;
  }

  const [video] = localVideos.splice(index, 1);

  if (video) {
    URL.revokeObjectURL(video.videoUrl);
  }
}
