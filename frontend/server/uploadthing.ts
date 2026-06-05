import { createUploadthing, type FileRouter } from "uploadthing/server";

const f = createUploadthing();

/**
 * Shared UploadThing file router.
 * `onUploadComplete` return value is sent to the browser `onClientUploadComplete`.
 * Logged server-side so your teammate can also wire a webhook / DB later.
 */
export const uploadRouter = {
  videoUploader: f({
    video: {
      maxFileSize: "1GB",
      maxFileCount: 1,
    },
  }).onUploadComplete(async ({ file }) => {
    const payload = {
      id: file.key,
      name: file.name,
      url: file.ufsUrl,
      size: file.size,
      uploadedAt: new Date().toISOString(),
    };

    console.log("[uploadthing] video uploaded:", payload);

    return payload;
  }),
} satisfies FileRouter;

export type UploadRouter = typeof uploadRouter;
