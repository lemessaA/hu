"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { Locale, Messages } from "./strings";
import { strings } from "./strings";

type Ctx = { locale: Locale; setLocale: (l: Locale) => void; t: Messages };

const I18nContext = createContext<Ctx | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");
  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    document.documentElement.lang = l === "am" ? "am" : "en";
  }, []);
  const value = useMemo(
    () => ({ locale, setLocale, t: strings[locale] }),
    [locale, setLocale]
  );
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): Ctx {
  const c = useContext(I18nContext);
  if (!c) throw new Error("useI18n requires provider");
  return c;
}
