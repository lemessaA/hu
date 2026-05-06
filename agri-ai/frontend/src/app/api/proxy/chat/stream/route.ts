import { NextResponse } from "next/server";
import { backendEnv, beHeaders } from "@/lib/server/backendEnv";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const body = await req.text();
  const { base } = backendEnv();
  const res = await fetch(`${base}/chat/stream`, {
    method: "POST",
    headers: beHeaders({ "Content-Type": "application/json" }),
    body,
  });
  return new NextResponse(res.body, {
    status: res.status,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
