// =====================================================================
// FILE: frontend/src/components/SearchableLanguageSelector.jsx
// DESCRIPTION: Premium searchable language selector dropdown component
//              supporting flag emojis, native names, keyboard navigation,
//              and dark mode styling.
// =====================================================================

import React, { useState, useEffect, useRef } from 'react';
import { Search, ChevronDown, Check } from 'lucide-react';

export const LANGUAGES = [
  { code: 'en', native: 'English', english: 'English', flag: '🇺🇸' },
  { code: 'hi', native: 'हिन्दी', english: 'Hindi', flag: '🇮🇳' },
  { code: 'bn', native: 'বাংলা', english: 'Bengali', flag: '🇮🇳' },
  { code: 'te', native: 'తెలుగు', english: 'Telugu', flag: '🇮🇳' },
  { code: 'ta', native: 'தமிழ்', english: 'Tamil', flag: '🇮🇳' },
  { code: 'kn', native: 'ಕನ್ನಡ', english: 'Kannada', flag: '🇮🇳' },
  { code: 'ml', native: 'മലയാളം', english: 'Malayalam', flag: '🇮🇳' },
  { code: 'pa', native: 'ਪੰਜਾਬੀ', english: 'Punjabi', flag: '🇮🇳' },
  { code: 'gu', native: 'ગુજરાતી', english: 'Gujarati', flag: '🇮🇳' },
  { code: 'mr', native: 'मराठी', english: 'Marathi', flag: '🇮🇳' },
  { code: 'ur', native: 'اردو', english: 'Urdu', flag: '🇵🇰' },
  { code: 'ne', native: 'नेपाली', english: 'Nepali', flag: '🇳🇵' },
  { code: 'si', native: 'සිංහල', english: 'Sinhala', flag: '🇱🇰' },
  { code: 'ar', native: 'العربية', english: 'Arabic', flag: '🇸🇦' },
  { code: 'fr', native: 'Français', english: 'French', flag: '🇫🇷' },
  { code: 'de', native: 'Deutsch', english: 'German', flag: '🇩🇪' },
  { code: 'es', native: 'Español', english: 'Spanish', flag: '🇪🇸' },
  { code: 'pt', native: 'Português', english: 'Portuguese', flag: '🇵🇹' },
  { code: 'it', native: 'Italiano', english: 'Italian', flag: '🇮🇹' },
  { code: 'nl', native: 'Nederlands', english: 'Dutch', flag: '🇳🇱' },
  { code: 'ru', native: 'Русский', english: 'Russian', flag: '🇷🇺' },
  { code: 'zh-CN', native: '简体中文', english: 'Chinese (Simplified)', flag: '🇨🇳' },
  { code: 'zh-TW', native: '繁體中文', english: 'Chinese (Traditional)', flag: '🇨🇳' },
  { code: 'ja', native: '日本語', english: 'Japanese', flag: '🇯🇵' },
  { code: 'ko', native: '한국어', english: 'Korean', flag: '🇰🇷' },
  { code: 'th', native: 'ไทย', english: 'Thai', flag: '🇹🇭' },
  { code: 'vi', native: 'Tiếng Việt', english: 'Vietnamese', flag: '🇻🇳' },
  { code: 'tr', native: 'Türkçe', english: 'Turkish', flag: '🇹🇷' },
  { code: 'fa', native: 'فارسی', english: 'Persian', flag: '🇮🇷' },
  { code: 'he', native: 'עברית', english: 'Hebrew', flag: '🇮🇱' },
  { code: 'id', native: 'Bahasa Indonesia', english: 'Indonesian', flag: '🇮🇩' },
  { code: 'ms', native: 'Bahasa Melayu', english: 'Malay', flag: '🇲🇾' },
  { code: 'sw', native: 'Kiswahili', english: 'Swahili', flag: '🇰🇪' },
  { code: 'pl', native: 'Polski', english: 'Polish', flag: '🇵🇱' },
  { code: 'uk', native: 'Українська', english: 'Ukrainian', flag: '🇺🇦' },
  { code: 'ro', native: 'Română', english: 'Romanian', flag: '🇷🇴' },
  { code: 'hu', native: 'Magyar', english: 'Hungarian', flag: '🇭🇺' },
  { code: 'cs', native: 'Čeština', english: 'Czech', flag: '🇨🇿' },
  { code: 'el', native: 'Ελληνικά', english: 'Greek', flag: '🇬🇷' },
  { code: 'fi', native: 'Suomi', english: 'Finnish', flag: '🇫🇮' },
  { code: 'no', native: 'Norsk', english: 'Norwegian', flag: '🇳🇴' },
  { code: 'sv', native: 'Svenska', english: 'Swedish', flag: '🇸🇪' },
  { code: 'da', native: 'Dansk', english: 'Danish', flag: '🇩🇰' },
  { code: 'is', native: 'Íslenska', english: 'Icelandic', flag: '🇮🇸' },
  { code: 'fil', native: 'Filipino', english: 'Filipino', flag: '🇵🇭' },
  { code: 'af', native: 'Afrikaans', english: 'Afrikaans', flag: '🇿🇦' },
  { code: 'zu', native: 'isiZulu', english: 'Zulu', flag: '🇿🇦' },
  { code: 'or', native: 'ଓଡ଼ିଆ', english: 'Odia', flag: '🇮🇳' }
];

export const SearchableLanguageSelector = ({ value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const containerRef = useRef(null);
  const searchInputRef = useRef(null);
  const listRef = useRef(null);
  const itemRefs = useRef([]);

  // Find active language
  const selectedLang = LANGUAGES.find(l => l.code === value) || LANGUAGES[0];

  // Filter languages
  const filtered = LANGUAGES.filter(l => 
    l.english.toLowerCase().includes(searchQuery.toLowerCase()) ||
    l.native.toLowerCase().includes(searchQuery.toLowerCase()) ||
    l.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Autofocus input on open
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        searchInputRef.current?.focus();
      }, 50);
      // Find current selected code inside filtered to highlight it
      const currentIdx = filtered.findIndex(l => l.code === value);
      setHighlightedIndex(currentIdx >= 0 ? currentIdx : 0);
    } else {
      setSearchQuery('');
    }
  }, [isOpen]);

  // Scroll active item into view during keyboard navigation
  useEffect(() => {
    if (isOpen && itemRefs.current[highlightedIndex]) {
      itemRefs.current[highlightedIndex].scrollIntoView({
        block: 'nearest',
        behavior: 'smooth'
      });
    }
  }, [highlightedIndex, isOpen]);

  // Handle Keyboard keys
  const handleKeyDown = (e) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === 'ArrowDown' || e.key === ' ') {
        e.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    if (e.key === 'Escape') {
      e.preventDefault();
      setIsOpen(false);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex(prev => (prev + 1) % filtered.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex(prev => (prev - 1 + filtered.length) % filtered.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[highlightedIndex]) {
        onChange(filtered[highlightedIndex].code);
        setIsOpen(false);
      }
    }
  };

  return (
    <div className="relative w-full text-left" ref={containerRef} onKeyDown={handleKeyDown}>
      
      {/* Selector Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 bg-white/50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs font-medium outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30 transition-all cursor-pointer text-slate-800 dark:text-slate-200"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm select-none">{selectedLang.flag}</span>
          <span className="font-semibold">{selectedLang.native}</span>
          <span className="opacity-60 text-slate-450 dark:text-slate-400">({selectedLang.english})</span>
        </div>
        <ChevronDown className="w-4 h-4 text-slate-400 select-none" />
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute left-0 right-0 mt-2 z-50 max-h-72 bg-white dark:bg-bg-panelDark border border-slate-200 dark:border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col backdrop-blur-xl animate-fade-in-down">
          
          {/* Search Box */}
          <div className="p-2 border-b border-slate-200/50 dark:border-white/5 flex items-center gap-2 relative bg-slate-50/50 dark:bg-white/[0.01]">
            <Search className="w-4 h-4 absolute left-4 text-slate-400 select-none pointer-events-none" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search language..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setHighlightedIndex(0);
              }}
              className="w-full pl-8.5 pr-4 py-2 bg-transparent text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-550 border-0 outline-none text-xs"
            />
          </div>

          {/* Languages List */}
          <ul
            ref={listRef}
            className="flex-1 overflow-y-auto p-1.5 max-h-52 divide-y divide-slate-100/30 dark:divide-white/[0.02]"
            role="listbox"
          >
            {filtered.length === 0 ? (
              <li className="px-4 py-6 text-center text-xs text-slate-400 dark:text-slate-550 select-none italic">
                No matching language found
              </li>
            ) : (
              filtered.map((lang, index) => {
                const isSelected = lang.code === value;
                const isHighlighted = index === highlightedIndex;

                return (
                  <li
                    key={lang.code}
                    ref={el => itemRefs.current[index] = el}
                    onClick={() => {
                      onChange(lang.code);
                      setIsOpen(false);
                    }}
                    onMouseEnter={() => setHighlightedIndex(index)}
                    className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl cursor-pointer text-xs select-none transition-colors ${
                      isHighlighted 
                        ? 'bg-emerald-600/10 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300 font-semibold' 
                        : isSelected 
                        ? 'bg-slate-100 dark:bg-white/5 text-slate-800 dark:text-white font-medium' 
                        : 'text-slate-650 dark:text-slate-350 hover:bg-slate-50 dark:hover:bg-white/[0.02]'
                    }`}
                    role="option"
                    aria-selected={isSelected}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-sm shrink-0">{lang.flag}</span>
                      <span>{lang.native}</span>
                      <span className="opacity-60 text-slate-450 dark:text-slate-500">({lang.english})</span>
                    </div>
                    {isSelected && <Check className="w-3.5 h-3.5 text-emerald-500 shrink-0" />}
                  </li>
                );
              })
            )}
          </ul>
        </div>
      )}
    </div>
  );
};
