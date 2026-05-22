import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Paleta Retrotarros synthwave
        magenta: '#FF2E88',
        cyan: '#00E5FF',
        purple: '#2D1B69',
        yellow: '#FFD23F',
        cream: '#F5F0E8',
        dark: '#06030F',
      },
      fontFamily: {
        display: ['Orbitron', 'system-ui', 'sans-serif'],
        mono: ['Share Tech Mono', 'ui-monospace', 'monospace'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;
