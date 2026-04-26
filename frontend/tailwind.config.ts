import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/**/*.{html,js,svelte,ts}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        headline: ['Space Grotesk', 'sans-serif'],
      },
      colors: {
        'neon-cyan': '#00d9ff',
        'neon-purple': '#9d4edd',
        'neon-pink': '#ff006e',
        'neon-blue': '#3a86ff',
        'dark-bg': '#060914',
        'card-bg': '#0d1120',
        'accent-1': '#7209b7',
        'accent-2': '#f72585',
        'on-background': '#f0f4ff',
        'on-surface': '#e8ecff',
        'on-surface-variant': '#b8bfd6',
        'surface-container-high': '#1a1f3a',
        'surface-bright': '#3a3f54',
        'outline': '#6b76a1',
        'outline-variant': '#364563',
        'primary': '#00d9ff',
      },
      boxShadow: {
        'neon-cyan': '0 0 20px rgba(0, 217, 255, 0.5)',
        'neon-purple': '0 0 20px rgba(157, 78, 221, 0.5)',
        'neon-pink': '0 0 20px rgba(247, 37, 133, 0.5)',
        'neon-blue': '0 0 20px rgba(58, 134, 255, 0.5)',
      },
      animation: {
        'pulse-neon': 'pulse-neon 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-neon': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 217, 255, 0.4)' },
          '50%': { boxShadow: '0 0 40px rgba(0, 217, 255, 0.8)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
