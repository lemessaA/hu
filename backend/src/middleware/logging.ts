import type { NextFunction, Request, Response } from "express";
import { randomUUID } from "crypto";

declare global {
  namespace Express {
    interface Request {
      requestId?: string;
    }
  }
}

export function loggingMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const requestId = randomUUID();
  req.requestId = requestId;
  const start = Date.now();
  res.setHeader("X-Request-Id", requestId);

  res.on("finish", () => {
    const ms = Date.now() - start;
    const line = {
      level: "info",
      requestId,
      method: req.method,
      path: req.path,
      status: res.statusCode,
      ms,
      ip: req.ip,
    };
    console.log(JSON.stringify(line));
  });

  next();
}
