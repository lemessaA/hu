"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { fetchRecentAdvice } from "./api";
import { readAdviceCache, writeAdviceCache } from "./offline";

export function useOnlineStatus() {
  const [online, setOnline] = useState(
    typeof navigator !== "undefined" ? navigator.onLine : true
  );
  useEffect(() => {
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);
  return online;
}

export function useRecentAdvice(online: boolean) {
  return useQuery({
    queryKey: ["advice", "recent"],
    queryFn: async () => {
      const data = await fetchRecentAdvice();
      writeAdviceCache(data.items);
      return data;
    },
    enabled: online,
    staleTime: 30_000,
    placeholderData: () => ({ items: readAdviceCache() }),
  });
}

export function useInvalidateAdvice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await qc.invalidateQueries({ queryKey: ["advice", "recent"] });
    },
  });
}

