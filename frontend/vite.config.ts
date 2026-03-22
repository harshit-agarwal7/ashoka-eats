import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'
import { copyFileSync, mkdirSync, readdirSync, existsSync } from 'fs'

function copyDataPlugin() {
  return {
    name: 'copy-data',
    buildStart() {
      const dataDir = resolve(__dirname, '../data')
      const dest = resolve(__dirname, 'public/data')
      if (!existsSync(dataDir)) return
      mkdirSync(dest, { recursive: true })
      for (const file of readdirSync(dataDir)) {
        if (file.endsWith('.json') && file !== 'raw_chunks.json') {
          copyFileSync(resolve(dataDir, file), resolve(dest, file))
        }
      }
    },
  }
}

export default defineConfig({
  plugins: [tailwindcss(), react(), copyDataPlugin()],
})
