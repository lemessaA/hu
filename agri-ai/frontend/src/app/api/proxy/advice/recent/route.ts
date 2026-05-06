import { NextResponse } from "next/server";
import { backendEnv, beHeaders } from "@/lib/server/backendEnv";

export const dynamic = "force-dynamic";

export async function GET() {
  const { base } = backendEnv();
  const res = await fetch(`${base}/advice/recent`, {
    headers: beHeaders(),
    cache: "no-store",
  });
  const text = await res.text();
  return new NextResponse(text, {
    status: res.status,
    headers: { "Content-Type": res.headers.get("content-type") || "application/json" },
  });
}
