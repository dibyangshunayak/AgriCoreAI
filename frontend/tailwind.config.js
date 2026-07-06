/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // AgriCore AI — ChatGPT-style dark palette
        primary: '#10B981',
        secondary: '#38BDF8',
        bg: {
          base: '#0F172A',
          sidebar: '#111827',
          card: '#1E293B',
          elevated: '#243347',
          // Legacy support
          light: '#f7fdf9',
          dark: '#0F172A',
          panel: '#ffffff',
          panelDark: '#1E293B',
        },
        text: {
          primary: '#FFFFFF',
          muted: '#94A3B8',
          faint: '#64748B',
        },
        border: {
          subtle: 'rgba(255,255,255,0.08)',
          focus: 'rgba(16,185,129,0.4)',
        },
        // Keep brand colors for any remaining references
        brand: {
          50: '#f1f8e9',
          100: '#dcedc8',
          200: '#c5e1a5',
          300: '#aed581',
          400: '#9ccc65',
          500: '#10B981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          accent: '#10B981',
          dark: '#064e3b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 1.5s infinite',
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.25s ease-out',
        'dot-bounce': 'dotBounce 1.4s ease-in-out infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        fadeIn: {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
        slideUp: {
          from: { opacity: 0, transform: 'translateY(8px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        dotBounce: {
          '0%, 80%, 100%': { transform: 'scale(0.6)', opacity: 0.4 },
          '40%': { transform: 'scale(1)', opacity: 1 },
        },
      },
      boxShadow: {
        'glass': '0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)',
        'sidebar': '4px 0 24px rgba(0,0,0,0.3)',
        'card': '0 2px 16px rgba(0,0,0,0.3)',
        'glow-green': '0 0 20px rgba(16,185,129,0.25)',
        'glow-blue': '0 0 20px rgba(56,189,248,0.25)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
