"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { useState } from "react";

const CopyButton = ({ text }: { text: string }) => {
  const [copied, setCopied] = useState(false);
  return (
    <button 
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="text-xs text-gray-400 hover:text-white transition-colors"
    >
      {copied ? "✓ Copied" : "Copy"}
    </button>
  );
};

export default function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="prose prose-invert max-w-none text-sm leading-relaxed prose-p:leading-relaxed prose-pre:p-0">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || "");
            return !inline && match ? (
              <div className="relative mt-2 mb-4 rounded-xl overflow-hidden bg-[#0D1117] border border-gray-800">
                <div className="flex items-center justify-between px-4 py-2 bg-[#161B22] border-b border-gray-800 text-xs text-gray-400">
                  <span className="font-mono">{match[1]}</span>
                  <CopyButton text={String(children).replace(/\n$/, "")} />
                </div>
                <SyntaxHighlighter
                  {...props}
                  style={oneDark}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    margin: 0,
                    padding: "1rem",
                    background: "transparent",
                    fontSize: "0.85rem",
                  }}
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              </div>
            ) : (
              <code {...props} className="bg-gray-800/50 px-1.5 py-0.5 rounded text-blue-200">
                {children}
              </code>
            );
          },
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          ul: ({ children }) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-4 mb-2">{children}</ol>,
          li: ({ children }) => <li className="mb-1">{children}</li>,
          a: ({ href, children }) => {
            if (href?.startsWith("#citation-")) {
              const num = href.replace("#citation-", "");
              return (
                <button
                  onClick={() => {/* future: scroll to source or highlight */}}
                  className="inline-flex w-4 h-4 bg-gray-700/80 rounded-full text-[9px] items-center justify-center -translate-y-2 ml-0.5 hover:bg-blue-600 transition-colors cursor-pointer text-white no-underline font-medium border border-gray-600/50"
                  title={`View Source ${num}`}
                >
                  {num}
                </button>
              );
            }
            return (
              <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                {children}
              </a>
            );
          },
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-gray-600 pl-3 italic text-gray-400 my-2">
              {children}
            </blockquote>
          ),
        }}
      >
        {content.replace(/\[(\d+)\]/g, "[$1](#citation-$1)")}
      </ReactMarkdown>
    </div>
  );
}
