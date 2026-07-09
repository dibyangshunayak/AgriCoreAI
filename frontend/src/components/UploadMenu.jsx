// =====================================================================
// FILE: frontend/src/components/UploadMenu.jsx
// DESCRIPTION: Glassmorphism upload dropdown with image, document, and
//              location options. Also handles drag-and-drop file events.
// =====================================================================

import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, MapPin, Image as ImageIcon } from 'lucide-react';
import { uploadFile, BACKEND_URL } from '../services/api';
import { useChat } from '../hooks/useChat';
import { useLocation } from '../hooks/useLocation';

export const UploadMenu = ({ isOpen, onClose }) => {
  const { setAttachmentDetails } = useChat();
  const { requestLocation } = useLocation();
  const imageInputRef = useRef(null);
  const docInputRef = useRef(null);

  // Handle drag-and-drop file events from ChatInput
  useEffect(() => {
    const handler = async (e) => {
      const file = e.detail?.file;
      if (!file) return;
      const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp'];
      const ext = file.name.split('.').pop().toLowerCase();
      if (!allowedExtensions.includes(ext)) {
        alert('Supported formats: JPG, JPEG, PNG, WEBP.');
        return;
      }
      try {
        const res = await uploadFile(file);
        const imageUrl = `${BACKEND_URL}/api/uploads/${res.file_name}`;
        setAttachmentDetails(res.file_path, res.file_name, res.type, res.context, imageUrl);
      } catch (err) {
        alert(`Error uploading image: ${err.message}`);
      }
    };
    window.addEventListener('agri:dropfile', handler);
    return () => window.removeEventListener('agri:dropfile', handler);
  }, [setAttachmentDetails]);

  if (!isOpen) return null;

  const handleImageSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    e.target.value = '';

    const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp'];
    const ext = file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(ext)) {
      alert('Supported formats: JPG, JPEG, PNG, WEBP.');
      return;
    }
    onClose();
    try {
      const res = await uploadFile(file);
      const imageUrl = `${BACKEND_URL}/api/uploads/${res.file_name}`;
      setAttachmentDetails(res.file_path, res.file_name, res.type, res.context, imageUrl);
    } catch (err) {
      alert(`Error uploading image: ${err.message}`);
    }
  };

  const handleDocSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    e.target.value = '';
    onClose();
    try {
      const res = await uploadFile(file);
      setAttachmentDetails(res.file_path, res.file_name, res.type, res.context);
    } catch (err) {
      alert(`Error uploading document: ${err.message}`);
    }
  };

  const handleLocationRequest = () => {
    onClose();
    requestLocation();
  };

  const menuItems = [
    {
      icon: ImageIcon,
      emoji: '📷',
      label: 'Upload Image',
      desc: 'JPG, PNG, WEBP',
      onClick: () => imageInputRef.current.click(),
    },
    {
      icon: FileText,
      emoji: '📄',
      label: 'Upload Document',
      desc: 'PDF, DOCX, TXT, CSV',
      onClick: () => docInputRef.current.click(),
    },
    {
      icon: MapPin,
      emoji: '📍',
      label: 'Use My Location',
      desc: 'GPS coordinates',
      onClick: handleLocationRequest,
    },
  ];

  return (
    <>
      {/* Hidden file inputs */}
      <input type="file" ref={imageInputRef} onChange={handleImageSelect}
        accept=".jpg,.jpeg,.png,.webp" className="hidden" />
      <input type="file" ref={docInputRef} onChange={handleDocSelect}
        accept=".pdf,.docx,.txt,.csv,.xlsx" className="hidden" />

      {/* Backdrop */}
      <div className="fixed inset-0 z-40" onClick={onClose} />

      {/* Menu */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ type: 'spring', damping: 22, stiffness: 320 }}
        className="absolute bottom-full left-0 mb-3 z-50 w-[220px] bg-[#1E293B] border border-white/10 rounded-2xl shadow-glass overflow-hidden"
      >
        <div className="p-1.5 flex flex-col gap-0.5">
          {menuItems.map(item => (
            <button
              key={item.label}
              onClick={item.onClick}
              className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-left hover:bg-white/10 transition-colors group"
            >
              <span className="text-lg">{item.emoji}</span>
              <div>
                <p className="text-[13px] text-white font-medium group-hover:text-[#10B981] transition-colors">{item.label}</p>
                <p className="text-[10px] text-[#64748B] mt-0.5">{item.desc}</p>
              </div>
            </button>
          ))}
        </div>
      </motion.div>
    </>
  );
};

export default UploadMenu;
