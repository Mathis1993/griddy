import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: '../griddy/static/js/vendored',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: 'main.js',
        styles: 'styles/vendor.css'
      },
      output: {
        // Disable Cache Busting here, as it will be Done by Django via the whitenoise
        // CompressedManifestStaticFilesStorage
        entryFileNames: '[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  }
});
