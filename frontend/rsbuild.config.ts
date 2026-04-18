import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";

export default defineConfig({
  plugins: [pluginReact()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: process.env.RSBUILD_APP_API_URL || "http://localhost:8000",
        changeOrigin: true,
      },
      "/health": {
        target: process.env.RSBUILD_APP_API_URL || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  output: {
    assetPrefix: "/",
  },
});
