"use client";

import { useState, useRef, useEffect } from "react";
import { useUIStore } from "@/stores/ui-store";
import { motion, AnimatePresence } from "framer-motion";

export default function ProfileDropdown() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const { openModal } = useUIStore();

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className="relative z-50">
      <button
        onClick={() => setOpen(!open)}
        className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 text-white flex items-center justify-center text-sm font-medium shadow-md transition-transform hover:scale-105"
      >
        A
      </button>

      <AnimatePresence>
        {open && (
          <motion.div 
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="absolute right-0 mt-3 w-56 bg-[#111827]/95 backdrop-blur-xl border border-gray-700/50 rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.5)] p-1.5 text-sm"
          >
            <div className="px-3 py-2.5 border-b border-gray-800/50 mb-1">
              <div className="font-semibold text-gray-200">Aman</div>
              <div className="text-xs text-gray-500">Free Plan</div>
            </div>

            <button className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-lg text-gray-300 transition-colors">
              Profile
            </button>

            <button
              onClick={() => { setOpen(false); openModal("settings"); }}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-lg text-gray-300 transition-colors flex items-center justify-between"
            >
              Settings
              <span className="text-[10px] text-gray-500 border border-gray-700 rounded px-1.5 py-0.5">⌘,</span>
            </button>

            <div className="my-1 border-t border-gray-800/50 mx-1" />

            <button
              onClick={() => { setOpen(false); openModal("upgrade"); }}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-lg text-blue-400 font-medium transition-colors flex items-center gap-2"
            >
              ✨ Upgrade Plan
            </button>

            <div className="my-1 border-t border-gray-800/50 mx-1" />

            <button className="w-full text-left px-3 py-2 hover:bg-red-500/10 hover:text-red-400 rounded-lg text-gray-400 transition-colors">
              Log out
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
