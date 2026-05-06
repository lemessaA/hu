"use client";

import { useI18n } from "@/lib/i18n";
import type { Locale } from "@/lib/strings";

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();
  const btn = (l: Locale, label: string) => (
    <button
      type="button"
      onClick={() => setLocale(l)}
      className={`rounded-full px-3 py-1 text-xs font-semibold ${
        locale === l
          ? "bg-agri-leaf text-white"
          : "bg-slate-100 text-slate-700 hover:bg-slate-200"
      }`}
    >
      {label}
    </button>
  );
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-slate-500">{t.language}:</span>
      {btn("en", t.en)}
      {btn("am", t.am)}
    </div>
  );
}
