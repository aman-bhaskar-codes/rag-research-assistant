export const MODE_CONFIG = {
  ai_research: {
    label: "AI Research",
    color: "from-purple-500 to-indigo-500",
    textDecoration: "text-purple-400",
    hint: "Focus on papers, citations, deep explanations",
    disabled: false,
  },
  programming: {
    label: "Programming",
    color: "from-green-500 to-emerald-500",
    textDecoration: "text-green-400",
    hint: "Code-first, structured answers, debugging",
    disabled: true,
    badge: "Coming Soon",
  },
  business: {
    label: "Business",
    color: "from-yellow-500 to-orange-500",
    textDecoration: "text-yellow-400",
    hint: "Insights, summaries, strategic thinking",
    disabled: true,
    badge: "Coming Soon",
  },
} as const;
