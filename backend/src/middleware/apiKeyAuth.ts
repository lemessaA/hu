import type { NextFunction, Request, Response } from "express";
import { config, isProduction } from "../config.js";

/**
 * Require X-API-Key header matching API_KEY when set, or always in production if API_KEY set.
 * In development, if API_KEY is empty, auth is skipped (local convenience).
 */
export function apiKeyAuth(req: Request, res: Response, next: NextFunction): void {
  if (!config.apiKey && !isProduction) {
    next();
    return;
  }
  if (!config.apiKey) {
    console.warn("[auth] API_KEY not set in production — refusing requests");
    res.status(503).json({
      error: "Server misconfiguration",
      code: "API_KEY_MISSING",
    });
    return;
  }
  const headerKey =
    req.header("x-api-key") ||
    (req.header("authorization")?.startsWith("Bearer ")
      ? req.header("authorization")!.slice(7)
      : undefined);
  if (headerKey !== config.apiKey) {
    res.status(401).json({ error: "Unauthorized", code: "INVALID_API_KEY" });
    return;
  }
  next();
}
