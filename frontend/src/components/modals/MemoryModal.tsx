"use client";

export default function MemoryModal() {
  const memory = [
    "User prefers highly technical, production-grade responses",
    "Interested in scalable RAG architectures",
    "Building an AI product with elite-level UX",
    "Prefers dark mode, glassmorphic interfaces",
  ];

  return (
    <div className="flex flex-col h-full text-left">
      <div className="mb-6 border-b border-gray-800 pb-4">
        <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-emerald-600">
          Memory Insights 🧠
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          Adaptive intelligence dynamically extracted from your conversations.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-2">
        {memory.map((m, i) => (
          <div
            key={i}
            className="p-4 bg-[#111827] border border-gray-800 rounded-xl text-sm shadow-sm flex items-start gap-3"
          >
            <span className="text-emerald-500 mt-0.5">•</span>
            <span className="text-gray-300 leading-relaxed max-w-[90%]">{m}</span>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-800 flex-shrink-0 text-center">
        <p className="text-xs text-gray-500">
          Memory extraction runs continuously in the background using Neo4j graph context.
        </p>
      </div>
    </div>
  );
}
