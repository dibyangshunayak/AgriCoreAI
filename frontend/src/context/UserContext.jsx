// =====================================================================
// FILE: frontend/src/context/UserContext.jsx
// DESCRIPTION: Lightweight localStorage-based user/profile context.
//              Replaces the old AuthContext. No authentication required.
//              All user data is stored locally in the browser.
// =====================================================================

import React, { createContext, useState, useContext, useEffect } from 'react';
import i18n from '../i18n';

const STORAGE_KEY = 'agri_user_profile';
const ONBOARDING_KEY = 'agri_onboarding_complete';

// Default empty profile
const DEFAULT_PROFILE = {
  name: '',
  farm_name: '',
  primary_crop: '',
  country: 'India',
  state: '',
  district: '',
  farm_location: '',
  preferred_language: 'en',
  theme: 'dark',
  farm_size: '',
  unit: 'hectares',
  soil_type: 'Loamy',
  irrigation: 'Rainfed',
  season: 'Kharif',
  secondary_crop: '',
  gps: null,
  notifications: {
    weather: true,
    disease: true,
    irrigation: true,
    schemes: true,
  },
};

/**
 * Load the stored profile from localStorage, merging with defaults
 * to ensure all fields are present even if stored profile is partial.
 */
const loadProfile = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      const savedTheme = localStorage.getItem('agri_theme');
      return { ...DEFAULT_PROFILE, ...parsed, theme: savedTheme || parsed.theme || DEFAULT_PROFILE.theme };
    }
  } catch (e) {
    console.warn('[UserContext] Failed to parse stored profile:', e);
  }
  return { ...DEFAULT_PROFILE };
};

const saveProfile = (profile) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
  } catch (e) {
    console.warn('[UserContext] Failed to save profile:', e);
  }
};

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [profile, setProfileState] = useState(() => loadProfile());

  // Sync language on mount and when language changes
  useEffect(() => {
    if (profile.preferred_language) {
      i18n.changeLanguage(profile.preferred_language);
    }
  }, [profile.preferred_language]);

  // Sync theme on mount and when theme changes
  useEffect(() => {
    const root = window.document.documentElement;
    if (profile.theme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
    try {
      localStorage.setItem('agri_theme', profile.theme);
    } catch (e) {
      console.warn('[UserContext] Failed to save theme:', e);
    }
  }, [profile.theme]);

  /**
   * Update profile fields (partial update) and persist to localStorage.
   */
  const updateProfile = (updates) => {
    setProfileState((prev) => {
      const next = { ...prev, ...updates };
      saveProfile(next);
      return next;
    });
  };

  /**
   * Replace entire profile and persist.
   */
  const setProfile = (newProfile) => {
    const merged = { ...DEFAULT_PROFILE, ...newProfile };
    saveProfile(merged);
    setProfileState(merged);
  };

  /**
   * Mark onboarding as completed (stored in a separate key).
   */
  const completeOnboarding = () => {
    try {
      localStorage.setItem(ONBOARDING_KEY, 'true');
    } catch (e) {
      console.warn('[UserContext] Failed to save onboarding flag:', e);
    }
  };

  /**
   * Check whether onboarding has been completed this session.
   */
  const isOnboardingComplete = () => {
    return localStorage.getItem(ONBOARDING_KEY) === 'true';
  };

  /**
   * Clear all local data (reset app to fresh state).
   */
  const clearProfile = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(ONBOARDING_KEY);
      localStorage.removeItem('agri_sessions');
      sessionStorage.clear();
    } catch (e) {
      console.warn('[UserContext] Failed to clear profile:', e);
    }
    setProfileState({ ...DEFAULT_PROFILE });
  };

  return (
    <UserContext.Provider
      value={{
        profile,
        updateProfile,
        setProfile,
        completeOnboarding,
        isOnboardingComplete,
        clearProfile,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error('useUser must be used inside <UserProvider>');
  return ctx;
};

export default UserContext;

