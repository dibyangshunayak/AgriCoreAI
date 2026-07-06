// =====================================================================
// FILE: frontend/src/i18n.js
// DESCRIPTION: Setup react-i18next configuration to lazy load locales.
// =====================================================================

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';

i18n
  .use(HttpBackend)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: [
      'en', 'hi', 'bn', 'te', 'ta', 'kn', 'ml', 'pa', 'gu', 'mr', 'ur', 'ne', 'si', 'ar', 'fr',
      'de', 'es', 'pt', 'it', 'nl', 'ru', 'zh-CN', 'zh-TW', 'ja', 'ko', 'th', 'vi', 'tr', 'fa',
      'he', 'id', 'ms', 'sw', 'pl', 'uk', 'ro', 'hu', 'cs', 'el', 'fi', 'no', 'sv', 'da', 'is',
      'fil', 'af', 'zu', 'or'
    ],
    ns: ['common', 'dashboard', 'chat', 'weather', 'settings'],
    defaultNS: 'common',
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    interpolation: {
      escapeValue: false, // React already safeguards against XSS
    },
    react: {
      useSuspense: false, // Turn off Suspense fallback to prevent white screens during loading
    }
  });

i18n.on('languageChanged', (lng) => {
  const rtlLanguages = ['ar', 'fa', 'he', 'ur'];
  const isRtl = rtlLanguages.includes(lng);
  document.documentElement.dir = isRtl ? 'rtl' : 'ltr';
  document.documentElement.lang = lng;
});

export default i18n;
