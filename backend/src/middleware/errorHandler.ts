import type { NextFunction, Request, Response } from "express";
import { ZodError } from "zod";

export function errorHandler(
  err: unknown,
  _req: Request,
  res: Response,
  _next: NextFunction
): void {
  if (err instanceof ZodError) {
    res.status(400).json({
      error: "Validation failed",
      code: "VALIDATION_ERROR",
      details: err.flatten(),
    });
    return;
  }
  const message = err instanceof Error ? err.message : "Internal error";
  console.error("[error]", err);
  res.status(500).json({
    error: "Internal server error",
    code: "INTERNAL",
    message:
      process.env.NODE_ENV === "production" ? undefined : message,
  });
}
