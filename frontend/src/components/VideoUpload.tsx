import { useState } from "react";
import { TbCheck, TbUpload } from "react-icons/tb";

import { UploadDropzone } from "@/lib/uploadthing";

import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

export type UploadedVideo = {
  id: string;
  name: string;
  url: string;
  size: number;
  uploadedAt: string;
};

function VideoUpload() {
  const [lastUpload, setLastUpload] = useState<UploadedVideo | null>(null);

  return (
    <Card className="w-full max-w-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TbUpload className="h-5 w-5 text-primary" />
          Upload video
        </CardTitle>
        <p className="text-sm text-foreground-secondary">MP4 and other video formats, up to 1GB. Files are stored on UploadThing.</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <UploadDropzone
          endpoint="videoUploader"
          onClientUploadComplete={(res) => {
            const file = res[0];
            if (!file) return;

            const uploaded: UploadedVideo = {
              id: file.serverData.id,
              name: file.serverData.name,
              url: file.serverData.url,
              size: file.serverData.size,
              uploadedAt: file.serverData.uploadedAt,
            };

            setLastUpload(uploaded);
          }}
          onUploadError={(error) => {
            console.error("Upload failed:", error);
            alert(error.message);
          }}
        />

        {lastUpload && (
          <div className="rounded-md border border-border bg-surface p-3 text-sm">
            <p className="mb-2 flex items-center gap-1 font-medium text-foreground">
              <TbCheck className="h-4 w-4 text-primary" />
              Ready for indexing
            </p>
            <p className="truncate text-foreground-secondary">{lastUpload.name}</p>
            <a
              className="mt-2 block truncate text-primary underline"
              href={lastUpload.url}
              rel="noreferrer"
              target="_blank"
            >
              {lastUpload.url}
            </a>
            <p className="mt-2 text-xs text-foreground-secondary">
              Share this URL with your teammate — or POST it to your pipeline from{" "}
              <code className="rounded bg-primary/10 px-1">onClientUploadComplete</code>.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default VideoUpload;
