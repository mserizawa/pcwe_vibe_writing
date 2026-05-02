import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

function serveLocalDirs() {
  const routes = [
    { prefix: '/shorts', dir: path.join(__dirname, '..', 'shorts') },
    { prefix: '/assets', dir: path.join(__dirname, '..', 'assets') },
  ]
  const mime = {
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
  }
  return {
    name: 'serve-local-dirs',
    configureServer(server) {
      for (const { prefix, dir } of routes) {
        server.middlewares.use(prefix, (req, res, next) => {
          const filePath = path.join(dir, req.url)
          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            res.setHeader('Content-Type', mime[path.extname(filePath)] ?? 'application/octet-stream')
            res.end(fs.readFileSync(filePath))
          } else {
            next()
          }
        })
      }
    },
  }
}

export default defineConfig({
  plugins: [tailwindcss(), react(), serveLocalDirs()],
})
