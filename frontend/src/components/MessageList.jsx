// =====================================================================
// FILE: frontend/src/components/MessageList.jsx
// DESCRIPTION: Scrollable message area with ChatGPT-style empty state
//              featuring 4 suggestion cards, and animated message list.
// =====================================================================

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MessageBubble from './MessageBubble';
import ThinkingLoader from './ThinkingLoader';
import { useChat } from '../hooks/useChat';

// ── Suggestion Cards ─────────────────────────────────────────────────
const SUGGESTIONS = [
  {
    icon: '🌾',
    title: 'Crop Disease Detection',
    desc: 'Identify diseases from leaf images',
    prompt: 'How do I detect and treat common crop diseases?',
  },
  {
    icon: '☁️',
    title: 'Weather Forecast',
    desc: 'Get local agriculture weather insights',
    prompt: 'What is the weather forecast for farming this week?',
  },
  {
    icon: '💰',
    title: 'Government Schemes',
    desc: 'Discover subsidies and benefits',
    prompt: 'What government schemes am I eligible for as a farmer?',
  },
  {
    icon: '📸',
    title: 'Analyze Plant Image',
    desc: 'Upload a photo for AI diagnostics',
    prompt: 'I want to analyze a plant image for disease diagnosis.',
  },
];

const SuggestionCard = ({ card, onClick }) => (
  <motion.button
    whileHover={{ y: -3, scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    transition={{ duration: 0.2 }}
    onClick={() => onClick(card.prompt)}
    className="suggestion-card flex flex-col items-start gap-2 p-4 bg-[#1E293B] border border-white/[0.08] rounded-2xl text-left cursor-pointer group"
  >
    <span className="text-2xl">{card.icon}</span>
    <div>
      <p className="text-sm font-semibold text-white group-hover:text-[#10B981] transition-colors">{card.title}</p>
      <p className="text-xs text-[#94A3B8] mt-0.5 leading-relaxed">{card.desc}</p>
    </div>
  </motion.button>
);

// ── MessageList ───────────────────────────────────────────────────────
export const MessageList = () => {
  const { messages, isThinking, isStreaming } = useChat();
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  // Find the global ChatInput textarea to pre-fill suggestion text
  const handleSuggestionClick = (prompt) => {
    // Dispatch a custom event that ChatInput listens to
    window.dispatchEvent(new CustomEvent('agri:suggest', { detail: { prompt } }));
  };

  return (
    <div className="flex-1 overflow-y-auto relative">
      {messages.length === 0 ? (
        // ── Empty State ──────────────────────────────────────────────
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          className="flex flex-col items-center justify-center min-h-full px-6 py-12 text-center"
        >
          <motion.h1
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-3xl md:text-4xl font-bold text-white mb-3 flex items-center gap-1 justify-center"
          >
            🌾AgriCore <span className="text-[#10B981]">AI</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-[#94A3B8] text-base md:text-lg mb-10 max-w-sm leading-relaxed"
          >
            Your intelligent agriculture assistant
          </motion.p>

          {/* Suggestion Cards */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl"
          >
            {SUGGESTIONS.map((card) => (
              <SuggestionCard key={card.title} card={card} onClick={handleSuggestionClick} />
            ))}
          </motion.div>
        </motion.div>
      ) : (
        // ── Messages ─────────────────────────────────────────────────
        <div className="max-w-3xl mx-auto px-4 md:px-6 py-6 space-y-1">
          <AnimatePresence initial={false}>
            {messages.map((message, index) => {
              const isLastMessage = index === messages.length - 1;
              const isStreamingLast = isLastMessage && message.role === 'assistant' && isStreaming;
              return (
                <motion.div
                  key={message.id || index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.22, ease: 'easeOut' }}
                >
                  <MessageBubble
                    message={message}
                    isStreamingLast={isStreamingLast}
                  />
                </motion.div>
              );
            })}
          </AnimatePresence>

          {/* Thinking loader */}
          <AnimatePresence>
            {isThinking && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 8 }}
                className="flex justify-start"
              >
                <ThinkingLoader />
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={bottomRef} className="h-4" />
        </div>
      )}
    </div>
  );
};

export default MessageList;
