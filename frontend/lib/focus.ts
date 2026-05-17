export interface FocusMode {
  id: string;
  label: string;
  icon: string;
  description: string;
  defaultModel: string;
  useWeb: boolean;
  useRag: boolean;
}

export const FOCUS_MODES: FocusMode[] = [
  {
    id: "general",
    label: "General",
    icon: "🔍",
    description: "Balanced web + document search",
    defaultModel: "llama3.2:3b",
    useWeb: true,
    useRag: true,
  },
  {
    id: "academic",
    label: "Academic",
    icon: "🎓",
    description: "Deep research with citations",
    defaultModel: "phi4-mini:latest",
    useWeb: true,
    useRag: true,
  },
  {
    id: "code",
    label: "Code",
    icon: "💻",
    description: "Programming and debugging",
    defaultModel: "phi4-mini:latest",
    useWeb: true,
    useRag: true,
  },
  {
    id: "writing",
    label: "Writing",
    icon: "✍️",
    description: "Your documents only",
    defaultModel: "llama3.2:3b",
    useWeb: false,
    useRag: true,
  },
  {
    id: "research",
    label: "Research",
    icon: "🔬",
    description: "Comprehensive web + RAG analysis",
    defaultModel: "phi4-mini:latest",
    useWeb: true,
    useRag: true,
  },
];
