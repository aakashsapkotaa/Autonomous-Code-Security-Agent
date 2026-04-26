import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [sveltekit()],
    server: {
      port: 5173,
      host: true,
    },
    define: {
      // Expose PUBLIC_API_URL as import.meta.env.PUBLIC_API_URL at runtime
      'import.meta.env.PUBLIC_API_URL': JSON.stringify(
        env.PUBLIC_API_URL || 'http://localhost:8000'
      ),
    },
  };
});
