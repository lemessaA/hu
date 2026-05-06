import dotenv from "dotenv";

dotenv.config();

const parseOrigins = (raw: string | undefined): string[] => {
  if (!raw?.trim()) return ["http://localhost:3000"];
  return raw.split(",").map((s) => s.trim()).filter(Boolean);
};

export const config = {
  port: Number(process.env.PORT) || 4000,
  nodeEnv: process.env.NODE_ENV || "development",
  apiKey: process.env.API_KEY || "",
  databaseUrl:
    process.env.DATABASE_URL ||
    "postgresql://postgres:postgres@localhost:5432/climate_agent",
  redisUrl: process.env.REDIS_URL || "redis://localhost:6379",
  openaiApiKey: process.env.OPENAI_API_KEY || "",
  openaiModel: process.env.OPENAI_MODEL || "gpt-4o-mini",
  corsOrigins: parseOrigins(process.env.CORS_ORIGINS),
  /** Max upload size in bytes (5 MB) */
  maxUploadBytes: 5 * 1024 * 1024,
};

export const isProduction = config.nodeEnv === "production";
