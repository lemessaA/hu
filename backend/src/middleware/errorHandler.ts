import type { NextFunction, Request, Response } from "express";
import { ZodError } from "zod";
import multer from "multer";

export function errorHandler(
  err: unknown,
  _req: Request,
  res: Response,
  _next: NextFunction
): void {
  if (err instanceof multer.MulterError) {
    res.status(400).json({
      error: "Upload error",
      code: err.code,
      message: err.message,
    });
    return;
  }
  if (err instanceof Error && err.message.startsWith("Invalid file type")) {
    res.status(400).json({
      error: "Invalid file type",
      code: "INVALID_FILE_TYPE",
      message: err.message,
    });
    return;
  }
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
