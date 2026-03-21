"use client";

import { useUIStore } from "@/stores/ui-store";
import SettingsModal from "./SettingsModal";
import UpgradeModal from "./UpgradeModal";
import CommandPalette from "./CommandPalette";
import MemoryModal from "./MemoryModal";
import { motion, AnimatePresence } from "framer-motion";

export default function ModalRoot() {
  const { activeModal, closeModal } = useUIStore();

  return (
    <AnimatePresence>
      {activeModal && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        >
          <motion.div 
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className={`bg-[#0B0F17] w-full shadow-2xl border border-gray-800 relative flex flex-col ${
              activeModal === "command"
                ? "max-w-lg mb-[20vh] rounded-2xl"
                : "max-w-[700px] h-[80vh] rounded-2xl p-6"
            }`}
          >
            {activeModal !== "command" && (
              <button
                onClick={closeModal}
                className="absolute top-4 right-4 text-gray-400 hover:text-white bg-gray-900 hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center transition-colors shadow-sm z-50"
              >
                ✕
              </button>
            )}

            <div className={`flex-1 overflow-hidden flex flex-col relative z-10 w-full h-full ${activeModal === "command" ? "" : "pt-2"}`}>
              {activeModal === "settings" && <SettingsModal />}
              {activeModal === "upgrade" && <UpgradeModal />}
              {activeModal === "memory" && <MemoryModal />}
              {activeModal === "command" && <CommandPalette />}
              {activeModal === "profile" && <div className="text-white p-4">Profile settings coming soon</div>}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
