import { NextResponse } from "next/server";
import { backendEnv, beHeaders } from "@/lib/server/backendEnv";
import { backendUnreachableResponse } from "@/lib/server/proxyErrors";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const body = await req.text();
  const { base } = backendEnv();
  let res: Response;
  try {
    res = await fetch(`${base}/chat`, {
      method: "POST",
      headers: beHeaders({ "Content-Type": "application/json" }),
      body,
    });
  } catch (e) {
    return backendUnreachableResponse(e);
  }
  const text = await res.text();
  return new NextResponse(text, {
    status: res.status,
    headers: { "Content-Type": res.headers.get("content-type") || "application/json" },
  });
}
