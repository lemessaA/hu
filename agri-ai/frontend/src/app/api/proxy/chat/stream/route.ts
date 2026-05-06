import { NextResponse } from "next/server";
import { backendEnv, beHeaders } from "@/lib/server/backendEnv";
import { backendUnreachableResponse } from "@/lib/server/proxyErrors";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const body = await req.text();
  const { base } = backendEnv();
  let res: Response;
  try {
    res = await fetch(`${base}/chat/stream`, {
      method: "POST",
      headers: beHeaders({ "Content-Type": "application/json" }),
      body,
    });
  } catch (e) {
    return backendUnreachableResponse(e);
  }
  return new NextResponse(res.body, {
    status: res.status,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
