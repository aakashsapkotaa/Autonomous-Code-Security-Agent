import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'neon-cyan': '#00d9ff',
        'neon-purple': '#9d4edd',
        'neon-pink': '#ff006e',
        'neon-blue': '#3a86ff',
        'dark-bg': '#0a0e27',
        'card-bg': '#151932',
        'accent-1': '#7209b7',
        'accent-2': '#f72585',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-hallway': 'linear-gradient(90deg, #0a0e27 0%, #1a0d35 50%, #0a0e27 100%)',
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
          '0%, 100%': { opacity: '1', textShadow: '0 0 20px rgba(0, 217, 255, 0.8)' },
          '50%': { opacity: '0.7', textShadow: '0 0 30px rgba(0, 217, 255, 0.4)' },
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
