import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e/tests',
  use: {
    baseURL: 'http://localhost:5173',
    headless: true,
  },
  reporter: [['list']],
});
