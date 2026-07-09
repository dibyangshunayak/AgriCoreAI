// =====================================================================
// FILE: frontend/src/components/ThinkingLoader.jsx
// DESCRIPTION: ChatGPT-style thinking indicator with avatar + three dots.
// =====================================================================

import React from 'react';
import { motion } from 'framer-motion';

export const ThinkingLoader = () => {
  return (
    <div className="flex gap-3 py-3">
      {/* Avatar */}
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#10B981] to-[#059669] flex items-center justify-center flex-shrink-0 shadow-glow-green mt-0.5">
        <motion.span
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          className="text-sm"
        >
          🌾
        </motion.span>
      </div>

      {/* Thinking dots */}
      <div className="flex items-center gap-2 bg-[#1E293B] border border-white/[0.08] rounded-2xl rounded-bl-md px-4 py-3 shadow-card">
        <div className="flex items-center gap-1.5">
          {[0, 1, 2].map(i => (
            <span
              key={i}
              className="thinking-dot w-2 h-2 rounded-full bg-[#10B981] block"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
        <span className="text-xs text-[#64748B] ml-1 select-none">AgriCore is thinking...</span>
      </div>
    </div>
  );
};

export default ThinkingLoader;
