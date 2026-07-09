// =====================================================================
// FILE: frontend/src/components/Sidebar.jsx
// DESCRIPTION: ChatGPT-style sidebar with chat history, search, and
//              session management. Pure UI — all data from ChatContext.
// =====================================================================

import React, { useState, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus, Search, MessageSquare, Settings, ChevronLeft,
  ChevronRight, MoreHorizontal, Pencil, Trash2, Pin,
  X, Check,
} from 'lucide-react';
import Logo from './Logo';
import { useChat } from '../hooks/useChat';

// ── Helpers ──────────────────────────────────────────────────────────
const groupSessionsByDate = (sessions) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const sevenDaysAgo = new Date(today);
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  const thirtyDaysAgo = new Date(today);
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

  const groups = { today: [], yesterday: [], previous7: [], previous30: [], older: [] };

  sessions.forEach(s => {
    const d = new Date(parseInt(s.id.split('_')[1]) || Date.now());
    if (d >= today) groups.today.push(s);
    else if (d >= yesterday) groups.yesterday.push(s);
    else if (d >= sevenDaysAgo) groups.previous7.push(s);
    else if (d >= thirtyDaysAgo) groups.previous30.push(s);
    else groups.older.push(s);
  });

  return groups;
};

// ── Chat Item ─────────────────────────────────────────────────────────
const ChatItem = ({ session, isActive, onSwitch, onRename, onDelete, onPin }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [renaming, setRenaming] = useState(false);
  const [renameVal, setRenameVal] = useState(session.name);

  const handleRenameSubmit = (e) => {
    e?.preventDefault();
    if (renameVal.trim()) onRename(session.id, renameVal.trim());
    setRenaming(false);
  };

  return (
    <div className="relative group">
      {renaming ? (
        <form onSubmit={handleRenameSubmit} className="flex items-center gap-1 px-2 py-1">
          <input
            autoFocus
            value={renameVal}
            onChange={e => setRenameVal(e.target.value)}
            onBlur={handleRenameSubmit}
            className="flex-1 bg-white/10 text-white text-xs rounded-lg px-2 py-1.5 outline-none border border-[#10B981]/40 min-w-0"
          />
          <button type="submit" className="p-1 text-[#10B981] hover:text-white">
            <Check className="w-3.5 h-3.5" />
          </button>
          <button type="button" onClick={() => setRenaming(false)} className="p-1 text-[#94A3B8] hover:text-white">
            <X className="w-3.5 h-3.5" />
          </button>
        </form>
      ) : (
        <button
          onClick={() => onSwitch(session.id)}
          className={`sidebar-item group w-full pr-8 ${isActive ? 'active' : ''}`}
        >
          <MessageSquare className="w-4 h-4 shrink-0 opacity-60" />
          <span className="flex-1 truncate text-left text-[13px]">{session.name}</span>
        </button>
      )}

      {/* Context menu trigger — visible on hover */}
      {!renaming && (
        <button
          onClick={(e) => { e.stopPropagation(); setMenuOpen(m => !m); }}
          className={`absolute right-1 top-1/2 -translate-y-1/2 p-1 rounded-md text-[#64748B] hover:text-white hover:bg-white/10 transition-all
            ${menuOpen ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}
        >
          <MoreHorizontal className="w-3.5 h-3.5" />
        </button>
      )}

      <AnimatePresence>
        {menuOpen && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -4 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -4 }}
              transition={{ duration: 0.12 }}
              className="absolute left-2 right-2 top-full mt-1 z-50 bg-[#1E293B] border border-white/10 rounded-xl shadow-xl overflow-hidden py-1"
            >
              <button
                onClick={() => { setRenaming(true); setMenuOpen(false); }}
                className="flex items-center gap-2.5 w-full px-3 py-2 text-xs text-[#94A3B8] hover:text-white hover:bg-white/10 transition-colors"
              >
                <Pencil className="w-3.5 h-3.5" /> Rename
              </button>
              <button
                onClick={() => { onPin(session.id); setMenuOpen(false); }}
                className="flex items-center gap-2.5 w-full px-3 py-2 text-xs text-[#94A3B8] hover:text-white hover:bg-white/10 transition-colors"
              >
                <Pin className="w-3.5 h-3.5" /> Pin
              </button>
              <div className="border-t border-white/5 my-0.5" />
              <button
                onClick={() => { onDelete(session.id); setMenuOpen(false); }}
                className="flex items-center gap-2.5 w-full px-3 py-2 text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" /> Delete
              </button>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

// ── Group Label ───────────────────────────────────────────────────────
const GroupLabel = ({ label }) => (
  <p className="px-3 pt-5 pb-1.5 text-[10px] font-semibold text-[#64748B] uppercase tracking-widest select-none">
    {label}
  </p>
);

// ── Sidebar ───────────────────────────────────────────────────────────
export const Sidebar = ({ isOpen, isCollapsed, onClose, onToggleCollapse }) => {
  const navigate = useNavigate();
  const routeLocation = useLocation();
  const { sessions, activeSessionId, createNewChat, switchChat, deleteChat, renameChat, pinChat } = useChat();

  const [search, setSearch] = useState('');

  const handleSwitch = (id) => {
    switchChat(id);
    navigate('/chat');
    if (window.innerWidth < 768) onClose();
  };

  const handleNew = () => {
    createNewChat();
    navigate('/chat');
    if (window.innerWidth < 768) onClose();
  };

  const filteredSessions = useMemo(() => {
    if (!search.trim()) return sessions;
    const q = search.toLowerCase();
    return sessions.filter(s => s.name.toLowerCase().includes(q));
  }, [sessions, search]);

  const grouped = useMemo(() => groupSessionsByDate(filteredSessions), [filteredSessions]);


  return (
    <>
      {/* Mobile backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-40 bg-black/60 md:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar container */}
      <aside
        className={`
          fixed md:relative top-0 left-0 z-50 h-screen flex-shrink-0 flex flex-col
          bg-[#111827] border-r border-white/[0.06] transition-all duration-300
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          ${isCollapsed ? 'w-[60px]' : 'w-[280px]'}
        `}
      >
        {/* ── Logo & Brand ── */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-white/[0.06] min-h-[64px] select-none">
          {!isCollapsed && (
            <span className="font-bold text-[16px] text-white tracking-tight flex items-center gap-1">
              🌾AgriCore <span className="text-[#10B981]">AI</span>
            </span>
          )}
          {isCollapsed && (
            <div className="text-lg mx-auto select-none">
              🌾
            </div>
          )}

          {/* Desktop collapse button */}
          <button
            onClick={onToggleCollapse}
            className="hidden md:flex p-1.5 rounded-lg text-[#64748B] hover:text-white hover:bg-white/10 transition-colors ml-auto"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {!isCollapsed && (
          <>
            {/* ── New Chat ── */}
            <div className="px-3 pt-4 pb-2">
              <button
                onClick={handleNew}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[#10B981] hover:bg-[#059669] text-white text-sm font-semibold rounded-xl transition-colors duration-150 shadow-glow-green"
              >
                <Plus className="w-4 h-4" />
                <span>New Chat</span>
              </button>
            </div>

            {/* ── Search ── */}
            <div className="px-3 pb-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#64748B]" />
                <input
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Search chats..."
                  className="w-full bg-white/[0.05] border border-white/10 rounded-lg pl-8 pr-3 py-2 text-xs text-white placeholder-[#64748B] outline-none focus:border-white/25 transition-colors"
                />
                {search && (
                  <button onClick={() => setSearch('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#64748B] hover:text-white">
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>

            {/* ── Chat History ── */}
            <div className="flex-1 overflow-y-auto px-2 pb-2">
              {/* Pinned */}
              {sessions.some(s => s.pinned) && (
                <>
                  <GroupLabel label="Pinned" />
                  {sessions.filter(s => s.pinned).map(s => (
                    <ChatItem
                      key={s.id} session={s}
                      isActive={s.id === activeSessionId}
                      onSwitch={handleSwitch}
                      onRename={renameChat}
                      onDelete={deleteChat}
                      onPin={pinChat}
                    />
                  ))}
                </>
              )}

              {grouped.today.length > 0 && (
                <>
                  <GroupLabel label="Today" />
                  {grouped.today.map(s => (
                    <ChatItem key={s.id} session={s} isActive={s.id === activeSessionId}
                      onSwitch={handleSwitch} onRename={renameChat} onDelete={deleteChat} onPin={pinChat} />
                  ))}
                </>
              )}
              {grouped.yesterday.length > 0 && (
                <>
                  <GroupLabel label="Yesterday" />
                  {grouped.yesterday.map(s => (
                    <ChatItem key={s.id} session={s} isActive={s.id === activeSessionId}
                      onSwitch={handleSwitch} onRename={renameChat} onDelete={deleteChat} onPin={pinChat} />
                  ))}
                </>
              )}
              {grouped.previous7.length > 0 && (
                <>
                  <GroupLabel label="Previous 7 Days" />
                  {grouped.previous7.map(s => (
                    <ChatItem key={s.id} session={s} isActive={s.id === activeSessionId}
                      onSwitch={handleSwitch} onRename={renameChat} onDelete={deleteChat} onPin={pinChat} />
                  ))}
                </>
              )}
              {grouped.previous30.length > 0 && (
                <>
                  <GroupLabel label="Previous 30 Days" />
                  {grouped.previous30.map(s => (
                    <ChatItem key={s.id} session={s} isActive={s.id === activeSessionId}
                      onSwitch={handleSwitch} onRename={renameChat} onDelete={deleteChat} onPin={pinChat} />
                  ))}
                </>
              )}
              {grouped.older.length > 0 && (
                <>
                  <GroupLabel label="Older" />
                  {grouped.older.map(s => (
                    <ChatItem key={s.id} session={s} isActive={s.id === activeSessionId}
                      onSwitch={handleSwitch} onRename={renameChat} onDelete={deleteChat} onPin={pinChat} />
                  ))}
                </>
              )}

              {filteredSessions.length === 0 && (
                <div className="text-center py-8 text-[#64748B] text-xs select-none">
                  {search ? 'No chats found' : 'No chat history'}
                </div>
              )}
            </div>

            {/* ── Bottom Nav ── */}
            <div className="border-t border-white/[0.06] p-3">
              <button
                onClick={() => { navigate('/settings'); if (window.innerWidth < 768) onClose(); }}
                className={`sidebar-item ${routeLocation.pathname === '/settings' ? 'active' : ''}`}
              >
                <Settings className="w-4 h-4 shrink-0" />
                <span className="text-[13px]">Settings</span>
              </button>
            </div>
          </>
        )}

        {/* Collapsed state — only icon buttons */}
        {isCollapsed && (
          <div className="flex-1 flex flex-col items-center gap-2 py-4">
            <button
              onClick={handleNew}
              title="New Chat"
              className="p-2.5 rounded-xl bg-[#10B981] hover:bg-[#059669] text-white transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
            <div className="flex-1" />
            <button
              onClick={() => navigate('/settings')}
              title="Settings"
              className={`p-2.5 rounded-xl transition-colors ${routeLocation.pathname === '/settings' ? 'bg-white/10 text-white' : 'text-[#64748B] hover:text-white hover:bg-white/10'}`}
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        )}
      </aside>
    </>
  );
};

export default Sidebar;





