import express from "express";
import cors from "cors";
import helmet from "helmet";
import { config } from "./config.js";
import { loggingMiddleware } from "./middleware/logging.js";
import { apiKeyAuth } from "./middleware/apiKeyAuth.js";
import { errorHandler } from "./middleware/errorHandler.js";
import { chatRouter } from "./routes/chat.js";
import { adviceRouter } from "./routes/advice.js";
import { ensureUploadDir, UPLOAD_DIR } from "./middleware/upload.js";

export function createApp(): express.Application {
  const app = express();

  app.use(helmet({ crossOriginResourcePolicy: { policy: "cross-origin" } }));
  app.use(
    cors({
      origin: config.corsOrigins,
      credentials: true,
    })
  );
  app.use(express.json({ limit: "1mb" }));
  app.use(loggingMiddleware);

  ensureUploadDir();
  app.use(
    "/uploads",
    express.static(UPLOAD_DIR, {
      maxAge: "1d",
      fallthrough: false,
    })
  );

  app.get("/health", (_req, res) => {
    res.json({ ok: true, service: "climate-agent-backend" });
  });

  app.use(apiKeyAuth);

  app.use("/api/chat", chatRouter);
  app.use("/api/advice", adviceRouter);

  app.use((_req, res) => {
    res.status(404).json({ error: "Not found", code: "NOT_FOUND" });
  });

  app.use(errorHandler);
  return app;
}
