"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ImageUploader } from "@/components/ImageUploader";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { MessageBubble } from "@/components/MessageBubble";
import { analyzeImage, sendChat, sendChatStream } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { useOnlineStatus } from "@/lib/hooks";

type Msg = { role: "user" | "assistant"; content: string };

function loadSession(): string {
  if (typeof window === "undefined") return "default";
  let s = localStorage.getItem("agri_session");
  if (!s) {
    s = crypto.randomUUID();
    localStorage.setItem("agri_session", s);
  }
  return s;
}

export function ChatUI() {
  const { t } = useI18n();
  const online = useOnlineStatus();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [location, setLocation] = useState("");
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [streamMode, setStreamMode] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [cropResult, setCropResult] = useState<Record<string, unknown> | null>(null);
  const [sid, setSid] = useState(loadSession);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const analyze = useCallback(async () => {
    if (!file || !online) return;
    setBusy(true);
    try {
      const res = await analyzeImage(file);
      setCropResult(res);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: String(e) },
      ]);
    } finally {
      setBusy(false);
    }
  }, [file, online]);

  const send = useCallback(async () => {
    if (!online || !input.trim()) return;
    const userText = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userText }]);
    setBusy(true);
    const payload = {
      message: userText,
      location: location.trim() || undefined,
      session_id: sid,
      crop_result: cropResult ?? undefined,
    };
    try {
      if (streamMode) {
        let acc = "";
        setMessages((m) => [...m, { role: "assistant", content: "" }]);
        await sendChatStream(
          payload,
          (tok) => {
            acc += tok;
            setMessages((m) => {
              const copy = [...m];
              copy[copy.length - 1] = { role: "assistant", content: acc };
              return copy;
            });
          },
          () => {}
        );
      } else {
        const res = await sendChat(payload);
        setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
      }
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: t.errorGeneric },
      ]);
    } finally {
      setBusy(false);
    }
  }, [online, input, location, sid, cropResult, streamMode, t]);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4 px-4 py-8">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-agri-leaf">{t.title}</h1>
          <p className="text-sm text-slate-600">{t.subtitle}</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <LanguageSwitcher />
          <nav className="flex gap-2 text-sm font-semibold">
            <Link className="text-agri-sky" href="/">
              {t.chat}
            </Link>
            <span className="text-slate-300">|</span>
            <Link className="text-agri-sky" href="/dashboard">
              {t.dashboard}
            </Link>
          </nav>
        </div>
      </header>

      {!online ? (
        <div className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900 ring-1 ring-amber-200">
          {t.offline}
        </div>
      ) : null}

      <div className="flex flex-wrap items-center gap-3 rounded-xl bg-white p-3 ring-1 ring-slate-200">
        <input
          className="min-w-[200px] flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm"
          placeholder={t.locationPh}
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          disabled={!online}
        />
        <label className="flex items-center gap-2 text-xs text-slate-600">
          <input
            type="checkbox"
            checked={streamMode}
            onChange={(e) => setStreamMode(e.target.checked)}
            disabled={!online}
          />
          Streaming
        </label>
        <button
          type="button"
          disabled={!online}
          className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-700"
          onClick={() => {
            setMessages([]);
            setCropResult(null);
            setFile(null);
            const n = crypto.randomUUID();
            localStorage.setItem("agri_session", n);
            setSid(n);
          }}
        >
          {t.newChat}
        </button>
      </div>

      <ImageUploader file={file} previewUrl={previewUrl} onFile={setFile} />
      <div className="flex gap-2">
        <button
          type="button"
          disabled={!online || !file || busy}
          onClick={analyze}
          className="rounded-lg bg-agri-sky px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        >
          {busy ? t.analyzing : t.analyze}
        </button>
        <button
          type="button"
          disabled
          title={t.voiceHint}
          className="rounded-lg border border-dashed border-slate-300 px-4 py-2 text-sm text-slate-400"
        >
          {t.voice}
        </button>
      </div>
      {cropResult ? (
        <pre className="max-h-40 overflow-auto rounded-lg bg-slate-900 p-3 text-xs text-emerald-100">
          {JSON.stringify(cropResult, null, 2)}
        </pre>
      ) : null}

      <div className="flex min-h-[320px] flex-col gap-3 rounded-2xl bg-white p-4 ring-1 ring-slate-200">
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} content={m.content} />
        ))}
        {busy && !streamMode ? (
          <p className="text-sm text-slate-500">{t.thinking}</p>
        ) : null}
      </div>

      <div className="flex gap-2">
        <textarea
          className="min-h-[96px] flex-1 resize-none rounded-xl border border-slate-200 px-3 py-2 text-sm"
          placeholder={t.messagePh}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!online || busy}
        />
        <button
          type="button"
          onClick={send}
          disabled={!online || busy || !input.trim()}
          className="self-end rounded-xl bg-agri-leaf px-5 py-3 text-sm font-semibold text-white disabled:opacity-50"
        >
          {busy ? (streamMode ? t.streaming : t.thinking) : t.send}
        </button>
      </div>
    </div>
  );
}
