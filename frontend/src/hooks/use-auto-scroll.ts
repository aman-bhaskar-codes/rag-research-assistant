"use client";

import { useRef, useEffect, useCallback, useState } from "react";

// ─── Auto-scroll Hook ────────────────────────────────────────────────────────

interface UseAutoScrollOptions {
  /** Pixel threshold from bottom above which auto-scroll is disabled */
  threshold?: number;
}

/**
 * Auto-scrolls a container to the bottom when content changes,
 * but respects user scroll override.
 *
 * If the user scrolls up past the threshold, auto-scroll pauses.
 * It resumes when the user scrolls back near the bottom.
 */
export function useAutoScroll<T extends HTMLElement>(
  deps: unknown[],
  options: UseAutoScrollOptions = {}
) {
  const { threshold = 100 } = options;
  const containerRef = useRef<T>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);

  const checkAtBottom = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
    setIsAtBottom(atBottom);
  }, [threshold]);

  // Scroll to bottom when deps change AND user hasn't scrolled up
  useEffect(() => {
    const el = containerRef.current;
    if (!el || !isAtBottom) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  // Listen for user scroll
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    el.addEventListener("scroll", checkAtBottom, { passive: true });
    return () => el.removeEventListener("scroll", checkAtBottom);
  }, [checkAtBottom]);

  /** Manually scroll to bottom (e.g. button click) */
  const scrollToBottom = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    setIsAtBottom(true);
  }, []);

  return { containerRef, isAtBottom, scrollToBottom };
}
