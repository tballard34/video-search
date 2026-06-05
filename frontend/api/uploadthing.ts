import { createRouteHandler } from "uploadthing/server";

import { uploadRouter } from "../server/uploadthing";

const handler = createRouteHandler({
  router: uploadRouter,
});

export const GET = handler;
export const POST = handler;
