import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Research Assistant — AI-Powered Search Engine",
  description: "Research assistant powered by local Ollama models + pgvector",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
