import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Providers } from "./providers";
import GlobalShortcuts from "@/components/ui/GlobalShortcuts";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "RAG Research Assistant",
  description:
    "AI-powered research assistant with retrieval-augmented generation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}>
      <body className="h-full flex flex-col bg-gradient-to-b from-[#020617] via-[#020617] to-[#0F172A] text-white overflow-hidden">
        <GlobalShortcuts />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
