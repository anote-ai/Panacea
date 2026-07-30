import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const buildMetadata = {
  service: "panacea-web",
  version: process.env.VITE_APP_VERSION || "1.0.0",
  commit:
    process.env.VITE_BUILD_SHA ||
    process.env.GITHUB_SHA ||
    process.env.COMMIT_SHA ||
    "unknown",
};

export default defineConfig({
  plugins: [
    react(),
    {
      name: "panacea-build-metadata",
      generateBundle() {
        this.emitFile({
          type: "asset",
          fileName: "build.json",
          source: `${JSON.stringify(buildMetadata, null, 2)}\n`,
        });
      },
    },
  ],
  server: {
    port: 3000,
    proxy: {
      "/api": { target: "http://localhost:5000", changeOrigin: true, timeout: 120000 },
      "/auth": { target: "http://localhost:5000", changeOrigin: true, timeout: 120000 },
      "/health": { target: "http://localhost:5000", changeOrigin: true, timeout: 120000 },
    },
  },
});
