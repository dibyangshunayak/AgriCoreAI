// =====================================================================
// FILE: frontend/src/pages/SettingsPage.jsx
// DESCRIPTION: ChatGPT-style settings page with dark card sections,
//              toggle switches, and smooth save feedback.
// =====================================================================

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import AppLayout from '../components/AppLayout';
import { SearchableLanguageSelector } from '../components/SearchableLanguageSelector';
import {
  Sun, Moon, Cpu, Trash2, Check,
  User,
} from 'lucide-react';
import { useUser } from '../context/UserContext';

// ── Section Card ──────────────────────────────────────────────────────
const SettingSection = ({ icon: Icon, title, children }) => (
  <div className="bg-[#1E293B] border border-white/[0.08] rounded-2xl overflow-visible">
    <div className="flex items-center gap-2.5 px-5 py-4 border-b border-white/[0.06]">
      <Icon className="w-4 h-4 text-[#10B981]" />
      <h3 className="text-sm font-semibold text-white">{title}</h3>
    </div>
    <div className="p-5 flex flex-col gap-4">
      {children}
    </div>
  </div>
);

// ── Toggle Row ────────────────────────────────────────────────────────
const ToggleRow = ({ label, description, checked, onChange }) => (
  <div className="flex items-center justify-between gap-4">
    <div className="flex-1 min-w-0">
      <p className="text-[13px] text-white font-medium">{label}</p>
      {description && <p className="text-[11px] text-[#64748B] mt-0.5 leading-relaxed">{description}</p>}
    </div>
    <input
      type="checkbox"
      checked={checked}
      onChange={onChange}
      className="toggle-switch flex-shrink-0"
    />
  </div>
);

// ── Field Row ─────────────────────────────────────────────────────────
const FieldRow = ({ label, children }) => (
  <div className="flex flex-col gap-2">
    <label className="text-[11px] font-semibold text-[#64748B] uppercase tracking-widest">{label}</label>
    {children}
  </div>
);

// ── Settings Page ─────────────────────────────────────────────────────
export const SettingsPage = () => {
  const { profile, updateProfile, clearProfile } = useUser();
  const navigate = useNavigate();

  const [name, setName] = useState(profile?.name || '');
  const [language, setLanguage] = useState(profile?.preferred_language || 'en');
  const [theme, setTheme] = useState(profile?.theme || 'dark');
  const [developerMode, setDeveloperMode] = useState(profile?.developer_mode ?? false);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState('');

  useEffect(() => {
    if (profile) {
      setName(profile.name || '');
      setLanguage(profile.preferred_language || 'en');
      setTheme(profile.theme || 'dark');
      setDeveloperMode(profile.developer_mode ?? false);
    }
  }, [profile]);

  // Live theme sync
  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') { root.classList.add('dark'); root.classList.remove('light'); }
    else { root.classList.add('light'); root.classList.remove('dark'); }
    try { localStorage.setItem('agri_theme', theme); } catch (e) { /* ignore */ }
  }, [theme]);


  const handleLanguageChange = (code) => {
    setLanguage(code);
    updateProfile({
      name,
      preferred_language: code,
      theme,
      developer_mode: developerMode,
    });
  };

  const handleSave = (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      updateProfile({
        name, preferred_language: language, theme, developer_mode: developerMode,
      });
      setToast('Settings saved successfully!');
      setTimeout(() => setToast(''), 3000);
    } catch {
      alert('Failed to save settings.');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm('This will clear all your profile data and reset to defaults. Are you sure?')) {
      clearProfile();
      window.location.href = '/chat';
    }
  };

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto py-2">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">Settings</h1>
          <p className="text-sm text-[#64748B] mt-1">Configure your AgriCore AI preferences</p>
        </div>

        {/* Toast */}
        <AnimatePresence>
          {toast && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="flex items-center gap-2.5 px-4 py-3 mb-4 bg-[#10B981]/15 border border-[#10B981]/25 rounded-xl text-[13px] text-[#10B981] font-medium"
            >
              <Check className="w-4 h-4" />
              {toast}
            </motion.div>
          )}
        </AnimatePresence>

        <form onSubmit={handleSave} className="flex flex-col gap-4">
          {/* Profile Section */}
          <SettingSection icon={User} title="Profile">
            <FieldRow label="Display Name">
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="e.g. John Doe"
                className="w-full px-4 py-2.5 bg-white/[0.05] border border-white/10 rounded-xl text-sm text-white placeholder-[#475569] outline-none focus:border-[#10B981]/50 transition-colors"
              />
            </FieldRow>

            <FieldRow label="Preferred Language">
              <SearchableLanguageSelector value={language} onChange={handleLanguageChange} />
            </FieldRow>
          </SettingSection>

          {/* Appearance Section */}
          <SettingSection icon={Sun} title="Appearance">
            <FieldRow label="Theme">
              <div className="flex gap-2">
                {[
                  { value: 'light', icon: Sun, label: 'Light' },
                  { value: 'dark', icon: Moon, label: 'Dark' },
                ].map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setTheme(opt.value)}
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium border transition-all cursor-pointer ${
                      theme === opt.value
                        ? 'bg-[#10B981] border-[#10B981] text-white'
                        : 'border-white/10 text-[#94A3B8] hover:bg-white/10 hover:text-white'
                    }`}
                  >
                    <opt.icon className="w-4 h-4" />
                    {opt.label}
                  </button>
                ))}
              </div>
            </FieldRow>
          </SettingSection>


          {/* Developer Section */}
          <SettingSection icon={Cpu} title="Developer Options">
            <ToggleRow
              label="Developer Mode"
              description="Show agent execution graphs, MCP call timelines, and raw AI logs in the chat interface"
              checked={developerMode}
              onChange={() => setDeveloperMode(v => !v)}
            />
          </SettingSection>

          {/* Actions */}
          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2.5 border border-rose-500/20 bg-rose-500/5 hover:bg-rose-500/15 text-rose-400 hover:text-rose-300 rounded-xl text-sm font-medium transition-all cursor-pointer"
            >
              <Trash2 className="w-4 h-4" />
              Reset All Data
            </button>

            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2.5 bg-[#10B981] hover:bg-[#059669] disabled:opacity-60 text-white rounded-xl text-sm font-semibold transition-all shadow-glow-green cursor-pointer"
            >
              {saving ? (
                <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              ) : (
                <Check className="w-4 h-4" />
              )}
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </AppLayout>
  );
};

export default SettingsPage;



