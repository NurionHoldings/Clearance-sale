import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests',
  testMatch: 'asia-logo.spec.mjs',
  use: { baseURL: 'http://127.0.0.1:8765', browserName: 'chromium', headless: true },
  webServer: { command: 'python3 -m http.server 8765 --bind 127.0.0.1', url: 'http://127.0.0.1:8765/asia-holdings-logo-demo.html', reuseExistingServer: !process.env.CI, timeout: 20000 },
  reporter: 'list',
});
