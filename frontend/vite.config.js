import { fileURLToPath, URL } from 'url';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import environment from 'vite-plugin-environment';

process.env.II_URL = process.env.II_URL || 'https://identity.internetcomputer.org/';
process.env.STORAGE_GATEWAY_URL = process.env.STORAGE_GATEWAY_URL || 'https://blob.caffeine.ai';

export default defineConfig({
    build: {
        emptyOutDir: true,
        sourcemap: false,
        minify: false
    },
    css: {
        postcss: './postcss.config.js'
    },
    optimizeDeps: {
        esbuildOptions: {
            define: {
                global: 'globalThis'
            }
        }
    },
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:4943',
                changeOrigin: true
            }
        }
    },
    plugins: [
        environment('all', { prefix: 'CANISTER_' }),
        environment('all', { prefix: 'DFX_' }),
        environment(['II_URL']),
        environment(['STORAGE_GATEWAY_URL']),
        react()
    ],
    resolve: {
        alias: [
            {
                find: 'declarations',
                replacement: fileURLToPath(new URL('./src/declarations', import.meta.url))
            },
            {
                find: '@',
                replacement: fileURLToPath(new URL('./src', import.meta.url))
            }
        ],
        dedupe: ['@dfinity/agent']
    }
});
