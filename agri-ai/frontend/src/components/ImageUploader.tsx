"use client";

import { useCallback, useRef, useState } from "react";
import { useI18n } from "@/lib/i18n";

type Props = {
  file: File | null;
  previewUrl: string | null;
  onFile: (f: File | null) => void;
};

export function ImageUploader({ file, previewUrl, onFile }: Props) {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);

  const pick = useCallback(
    (f: File | null) => {
      if (f && !f.type.startsWith("image/")) return;
      onFile(f);
    },
    [onFile]
  );

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-slate-700">{t.attach}</p>
      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          const f = e.dataTransfer.files?.[0];
          pick(f ?? null);
        }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-4 py-6 text-center text-sm transition ${
          drag ? "border-agri-leaf bg-emerald-50" : "border-slate-300 bg-white"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => pick(e.target.files?.[0] ?? null)}
        />
        {previewUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={previewUrl}
            alt={t.preview}
            className="mb-2 max-h-40 rounded-lg object-contain"
          />
        ) : null}
        <span className="text-slate-600">{t.drop}</span>
        {file ? (
          <button
            type="button"
            className="mt-3 text-xs font-semibold text-red-600"
            onClick={(e) => {
              e.stopPropagation();
              pick(null);
            }}
          >
            {t.remove}
          </button>
        ) : null}
      </div>
    </div>
  );
}
