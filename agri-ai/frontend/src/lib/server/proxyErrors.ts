import { NextResponse } from "next/server";
import { backendEnv } from "./backendEnv";

/**
 * JSON response when fetch() to FastAPI fails (ECONNREFUSED, etc.).
 */
export function backendUnreachableResponse(err: unknown): NextResponse {
  const { base } = backendEnv();
  let detail = err instanceof Error ? err.message : String(err);
  const c = err instanceof Error ? err.cause : undefined;
  if (c instanceof Error) {
    detail = `${detail}: ${c.message}`;
  }
  return NextResponse.json(
    {
      error: "BACKEND_UNREACHABLE",
      message: "Next.js could not connect to the FastAPI backend.",
      detail,
      backend_url: base,
      hint:
        "Run both servers: from the agri-ai folder use `npm run dev` (starts API + UI). If the API exits immediately, check Postgres/Redis and DATABASE_URL in .env.",
    },
    { status: 503 }
  );
}
