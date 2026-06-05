import { generateReactHelpers, generateUploadButton, generateUploadDropzone } from "@uploadthing/react";

import type { UploadRouter } from "../../server/uploadthing";

const apiUrl = import.meta.env.VITE_UPLOADTHING_API_URL ?? "/api/uploadthing";

export const UploadButton = generateUploadButton<UploadRouter>({ url: apiUrl });
export const UploadDropzone = generateUploadDropzone<UploadRouter>({ url: apiUrl });
export const { useUploadThing, uploadFiles } = generateReactHelpers<UploadRouter>({ url: apiUrl });
