"use client";

import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useI18n } from "@/lib/i18n";
import { readAdviceCache } from "@/lib/offline";
import { useOnlineStatus, useRecentAdvice } from "@/lib/hooks";

export default function DashboardPage() {
  const { t } = useI18n();
  const online = useOnlineStatus();
  const qc = useQueryClient();
  const q = useRecentAdvice(online);
  const cached = readAdviceCache();
  const items =
    q.data?.items && q.data.items.length > 0 ? q.data.items : cached;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-agri-leaf">{t.dashboard}</h1>
          <p className="text-sm text-slate-600">{t.dashboardNote}</p>
        </div>
        <div className="flex items-center gap-3">
          <LanguageSwitcher />
          <Link href="/" className="text-sm font-semibold text-agri-sky">
            ← {t.chat}
          </Link>
          <button
            type="button"
            className="rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white"
            onClick={() => qc.invalidateQueries({ queryKey: ["advice", "recent"] })}
          >
            {t.refresh}
          </button>
        </div>
      </header>

      {!online ? (
        <p className="mb-4 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">
          {t.offline}
        </p>
      ) : null}

      {q.isLoading ? (
        <p className="text-sm text-slate-500">{t.thinking}</p>
      ) : null}
      {q.error ? (
        <p className="text-sm text-red-600">{t.errorGeneric}</p>
      ) : null}

      <ul className="space-y-3">
        {items.map((it, idx) => (
          <li
            key={`${it.created_at}-${idx}`}
            className="rounded-xl bg-white p-4 text-sm shadow-sm ring-1 ring-slate-200"
          >
            <p className="text-xs text-slate-400">{it.created_at}</p>
            <p className="mt-2 whitespace-pre-wrap text-slate-800">{it.content}</p>
          </li>
        ))}
      </ul>

      {!items.length && !q.isLoading ? (
        <p className="text-slate-500">{t.noAdvice}</p>
      ) : null}
    </div>
  );
}
