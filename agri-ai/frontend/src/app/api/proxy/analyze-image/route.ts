import { NextResponse } from "next/server";
import { backendEnv, beHeaders } from "@/lib/server/backendEnv";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const form = await req.formData();
  const { base } = backendEnv();
  const res = await fetch(`${base}/analyze-image`, {
    method: "POST",
    headers: beHeaders(),
    body: form,
  });
  const text = await res.text();
  return new NextResponse(text, {
    status: res.status,
    headers: { "Content-Type": res.headers.get("content-type") || "application/json" },
  });
}
