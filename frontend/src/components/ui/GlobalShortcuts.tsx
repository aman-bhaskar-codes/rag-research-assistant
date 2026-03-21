"use client";

import { useEffect } from "react";
import { useUIStore } from "@/stores/ui-store";

export default function GlobalShortcuts() {
  const { openModal } = useUIStore();

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        openModal("command");
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [openModal]);

  return null;
}
