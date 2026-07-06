// =====================================================================
// FILE: frontend/src/components/ChatInput.jsx
// DESCRIPTION: ChatGPT-style input bar with auto-grow textarea,
//              attachment support, drag-and-drop, and suggestion events.
// =====================================================================

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { Paperclip, ArrowUp, Mic, MapPin } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { useStreaming } from '../hooks/useStreaming';
import UploadMenu from './UploadMenu';
import ImagePreview from './ImagePreview';

export const ChatInput = () => {
  const { t } = useTranslation(['chat']);
  const { attachment, removeAttachment, isThinking, isStreaming } = useChat();
  const { sendMessage } = useStreaming();

  const [inputVal, setInputVal] = useState('');
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const textareaRef = useRef(null);
  const isBusy = isThinking || isStreaming;
  const isSendDisabled = (!inputVal.trim() && !attachment) || isBusy;

  // ── Auto-resize textarea ──
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 180) + 'px';
    }
  }, [inputVal]);

  // ── Listen for suggestion card clicks ──
  useEffect(() => {
    const handler = (e) => {
      setInputVal(e.detail.prompt);
      setTimeout(() => textareaRef.current?.focus(), 50);
    };
    window.addEventListener('agri:suggest', handler);
    return () => window.removeEventListener('agri:suggest', handler);
  }, []);

  // ── Send handler ──
  const handleSend = useCallback(() => {
    const trimmed = inputVal.trim();
    if ((!trimmed && !attachment) || isBusy) return;
    sendMessage(trimmed);
    setInputVal('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  }, [inputVal, attachment, isBusy, sendMessage]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ── Drag & Drop ──
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = () => setIsDragging(false);
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      // Dispatch to UploadMenu logic by opening with a file ready
      window.dispatchEvent(new CustomEvent('agri:dropfile', { detail: { file } }));
    }
  };

  return (
    <div
      className="flex-shrink-0 relative"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Gradient fade-out above input */}
      <div className="absolute bottom-full left-0 right-0 h-16 bg-gradient-to-t from-[#0F172A] to-transparent pointer-events-none" />

      <div className="relative px-4 md:px-6 pb-6 pt-2 bg-[#0F172A]">
        <div className="max-w-3xl mx-auto">
          {/* Attachment Preview */}
          <AnimatePresence>
            {attachment && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 8 }}
                className="mb-3"
              >
                <ImagePreview attachment={attachment} onRemove={removeAttachment} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Drag overlay */}
          <AnimatePresence>
            {isDragging && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 z-50 flex items-center justify-center bg-[#0F172A]/90 border-2 border-dashed border-[#10B981] rounded-2xl m-4"
              >
                <div className="text-center">
                  <p className="text-[#10B981] font-semibold text-sm">Drop image here</p>
                  <p className="text-[#94A3B8] text-xs mt-1">JPG, PNG, WEBP supported</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Main input container */}
          <div className={`relative flex flex-col glass-input rounded-2xl transition-all duration-200
            ${isBusy ? 'opacity-70' : 'focus-within:border-white/25 focus-within:shadow-glow-green/20'}`}
          >
            {/* Textarea row */}
            <div className="flex items-end px-3 py-2.5 gap-2">
              {/* Attachment button */}
              <div className="relative flex-shrink-0">
                <button
                  onClick={() => setIsUploadOpen(o => !o)}
                  disabled={isBusy}
                  className="p-2 rounded-xl text-[#64748B] hover:text-white hover:bg-white/10 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                  aria-label="Add attachment"
                >
                  <Paperclip className={`w-5 h-5 transition-transform duration-200 ${isUploadOpen ? 'rotate-45 text-[#10B981]' : ''}`} />
                </button>

                <AnimatePresence>
                  {isUploadOpen && (
                    <UploadMenu isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />
                  )}
                </AnimatePresence>
              </div>

              {/* Auto-grow textarea */}
              <textarea
                ref={textareaRef}
                rows={1}
                value={inputVal}
                onChange={e => setInputVal(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything about agriculture..."
                disabled={isBusy}
                aria-label="Message input"
                className="flex-1 min-h-[36px] max-h-[180px] resize-none bg-transparent outline-none border-none text-[14px] text-white placeholder-[#64748B] leading-relaxed py-2 font-sans"
              />

              {/* Right actions */}
              <div className="flex items-center gap-1 flex-shrink-0">
                {/* Send / Stop */}
                <motion.button
                  onClick={handleSend}
                  disabled={isSendDisabled}
                  whileHover={!isSendDisabled ? { scale: 1.08 } : {}}
                  whileTap={!isSendDisabled ? { scale: 0.93 } : {}}
                  className={`p-2.5 rounded-xl transition-all duration-200 ${
                    isSendDisabled
                      ? 'bg-white/5 text-[#475569] cursor-not-allowed'
                      : 'bg-[#10B981] hover:bg-[#059669] text-white shadow-glow-green cursor-pointer'
                  }`}
                  aria-label="Send message"
                >
                  {isBusy ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <ArrowUp className="w-4 h-4" />
                  )}
                </motion.button>
              </div>
            </div>
          </div>

          {/* Footer hint */}
          <p className="text-center text-[11px] text-[#475569] mt-2.5 select-none">
            AgriCore AI · Press <kbd className="px-1 py-0.5 bg-white/5 rounded text-[10px] font-mono">Enter</kbd> to send · <kbd className="px-1 py-0.5 bg-white/5 rounded text-[10px] font-mono">Shift+Enter</kbd> for new line
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
