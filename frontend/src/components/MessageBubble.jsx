// =====================================================================
// FILE: frontend/src/components/MessageBubble.jsx
// DESCRIPTION: ChatGPT-style message bubbles with react-markdown,
//              syntax highlighting, avatars, and streaming cursor.
// =====================================================================

import React, { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import Logo from './Logo';

// ── Code Block Component ─────────────────────────────────────────────
const CodeBlock = ({ node, inline, className, children, ...props }) => {
  const match = /language-(\w+)/.exec(className || '');
  const lang = match ? match[1] : 'text';

  if (inline) {
    return (
      <code className="bg-white/10 text-[#38BDF8] rounded px-1.5 py-0.5 text-[13px] font-mono" {...props}>
        {children}
      </code>
    );
  }

  return (
    <div className="my-3 rounded-xl overflow-hidden border border-white/10">
      {/* Code header */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#0F172A] border-b border-white/10">
        <span className="text-[11px] text-[#94A3B8] font-mono uppercase tracking-wider">{lang}</span>
        <button
          onClick={() => navigator.clipboard?.writeText(String(children))}
          className="text-[11px] text-[#94A3B8] hover:text-white transition-colors font-medium"
        >
          Copy
        </button>
      </div>
      <SyntaxHighlighter
        style={oneDark}
        language={lang}
        PreTag="div"
        customStyle={{
          margin: 0,
          borderRadius: 0,
          background: '#0a1628',
          padding: '16px',
          fontSize: '13px',
          lineHeight: '1.6',
        }}
        {...props}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    </div>
  );
};

// ── Markdown Components Config ────────────────────────────────────────
const markdownComponents = {
  code: CodeBlock,
  h1: ({ children }) => <h1 className="text-xl font-bold text-white mb-3 mt-4 border-b border-white/10 pb-2">{children}</h1>,
  h2: ({ children }) => <h2 className="text-lg font-bold text-white mb-2 mt-4">{children}</h2>,
  h3: ({ children }) => <h3 className="text-base font-semibold text-white mb-2 mt-3">{children}</h3>,
  p: ({ children }) => <p className="text-[14px] text-[#CBD5E1] leading-relaxed mb-3 last:mb-0">{children}</p>,
  ul: ({ children }) => <ul className="list-disc pl-5 my-2 space-y-1.5">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-5 my-2 space-y-1.5">{children}</ol>,
  li: ({ children }) => <li className="text-[14px] text-[#CBD5E1] leading-relaxed">{children}</li>,
  strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
  em: ({ children }) => <em className="italic text-[#94A3B8]">{children}</em>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-[#10B981] pl-4 my-3 text-[#94A3B8] italic">
      {children}
    </blockquote>
  ),
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer"
      className="text-[#38BDF8] underline underline-offset-2 hover:text-white transition-colors">
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="my-3 overflow-x-auto rounded-xl border border-white/10">
      <table className="w-full text-sm border-collapse">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-white/10">{children}</thead>,
  th: ({ children }) => (
    <th className="px-3 py-2.5 text-left text-xs font-semibold text-white border-b border-white/10 whitespace-nowrap">{children}</th>
  ),
  td: ({ children }) => (
    <td className="px-3 py-2 text-[#CBD5E1] text-xs border-b border-white/[0.05] last:border-0">{children}</td>
  ),
  tr: ({ children }) => <tr className="hover:bg-white/[0.03] transition-colors">{children}</tr>,
  hr: () => <hr className="border-white/10 my-4" />,
  img: ({ src, alt }) => (
    <img src={src} alt={alt} className="max-w-full rounded-xl border border-white/10 my-3" />
  ),
};

// ── AgriCore Avatar ───────────────────────────────────────────────────
const AgriAvatar = () => (
  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#10B981] to-[#059669] flex items-center justify-center flex-shrink-0 shadow-glow-green mt-0.5">
    <span className="text-sm">🌾</span>
  </div>
);

// ── Message Bubble ────────────────────────────────────────────────────
export const MessageBubble = memo(({ message, isStreamingLast }) => {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 py-3 group">
        <div className="flex flex-col items-end max-w-[75%] md:max-w-[65%]">
          {/* User bubble */}
          <div className="bg-[#10B981] text-white rounded-2xl rounded-br-md px-4 py-3 shadow-sm">
            {/* Attached image */}
            {message.image && (
              <div className="mb-2 overflow-hidden rounded-xl border border-white/20 max-w-[300px]">
                <img
                  src={message.image}
                  alt="Uploaded"
                  className="w-full h-auto object-cover max-h-[240px]"
                />
              </div>
            )}
            {message.content && (
              <p className="text-[14px] leading-relaxed whitespace-pre-wrap select-text">{message.content}</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ── Assistant message ──
  return (
    <div className="flex justify-start gap-3 py-3 group">
      <div className="flex flex-col items-start max-w-[85%] md:max-w-[75%]">
        {/* Card Bubble Container */}
        <div className="glass text-white rounded-2xl rounded-bl-md px-5 py-4 border border-white/10 shadow-sm w-full">
          {/* Header with icon and name */}
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm font-semibold text-[#10B981] flex items-center gap-1.5 select-none">
              🌾 AgriCore AI
            </span>
          </div>

          {/* Content */}
          <div className="text-[14px] text-[#CBD5E1] leading-relaxed">
            {message.content ? (
              <div className="markdown-body">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={markdownComponents}
                >
                  {message.content}
                </ReactMarkdown>
                {isStreamingLast && (
                  <span className="blinking-cursor" aria-hidden="true" />
                )}
              </div>
            ) : isStreamingLast ? (
              <span className="blinking-cursor" aria-hidden="true" />
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
});

MessageBubble.displayName = 'MessageBubble';
export default MessageBubble;
