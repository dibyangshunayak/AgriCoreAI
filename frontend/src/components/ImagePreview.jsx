// =====================================================================
// FILE: frontend/src/components/ImagePreview.jsx
// DESCRIPTION: Compact attachment preview with scan animation.
// =====================================================================

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, FileText, MapPin, Image as ImageIcon, Check, Loader2 } from 'lucide-react';

export const ImagePreview = ({ attachment, onRemove }) => {
  if (!attachment) return null;

  const isImage = attachment.type === 'image';

  return (
    <div className="flex flex-col gap-2 max-w-sm">
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 6 }}
        className="relative flex items-center gap-3 p-3 bg-[#1E293B] border border-white/10 rounded-xl overflow-hidden"
      >
        {/* Thumbnail */}
        <div className="relative w-11 h-11 rounded-lg bg-[#0F172A] flex items-center justify-center overflow-hidden flex-shrink-0 border border-white/10">
          {isImage && attachment.previewUrl ? (
            <img src={attachment.previewUrl} alt="Preview" className="w-full h-full object-cover" />
          ) : isImage ? (
            <ImageIcon className="w-5 h-5 text-[#10B981]" />
          ) : attachment.type === 'gps' ? (
            <MapPin className="w-5 h-5 text-[#38BDF8]" />
          ) : (
            <FileText className="w-5 h-5 text-[#94A3B8]" />
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0 pr-5">
          <p className="text-[13px] font-semibold text-white truncate">{attachment.file_name}</p>
          <p className="text-[11px] text-[#64748B] mt-0.5 truncate">
            {attachment.context || 'Ready to send'}
          </p>
        </div>

        {/* Remove */}
        <button
          onClick={onRemove}
          className="absolute top-2 right-2 w-5 h-5 flex items-center justify-center rounded-full bg-white/10 hover:bg-rose-500/80 text-[#94A3B8] hover:text-white transition-all"
          aria-label="Remove attachment"
        >
          <X className="w-3 h-3" />
        </button>
      </motion.div>
    </div>
  );
};

export default ImagePreview;
