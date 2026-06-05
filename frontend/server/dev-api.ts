import cors from "cors";
import express from "express";
import { createRouteHandler } from "uploadthing/express";

import { uploadRouter } from "./uploadthing";

const app = express();
const port = Number(process.env.UPLOADTHING_DEV_PORT ?? 3001);

app.use(
  cors({
    origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
  }),
);

app.use(
  "/api/uploadthing",
  createRouteHandler({
    router: uploadRouter,
  }),
);

app.get("/health", (_req, res) => {
  res.json({ ok: true });
});

app.listen(port, () => {
  console.log(`UploadThing dev API listening on http://localhost:${port}`);
});
