/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// `base: './'` so the built page opens from any directory — `dashboard/app/index.html` over
// file:// or python's http.server, and firebase hosting's root alike (DESIGN-ship-1 §2).
// The build writes into `dashboard/app/`, which `scripts/export_front_data.py --stage` then fills
// with `data/`: vite empties its own output directory, so the copy has to come after it.
export default defineConfig({
  base: './',
  plugins: [react()],
  build: { outDir: '../dashboard/app', emptyOutDir: true, sourcemap: false },
  test: {
    // `globals: true` is the runtime half of tsconfig's `types: ["vitest/globals"]`: the types
    // alone typecheck `describe`/`it`/`expect` and inject nothing, so the suite would throw a
    // ReferenceError on its first line.
    globals: true,
    environment: 'node',
    include: ['test/**/*.test.ts'],
  },
})
