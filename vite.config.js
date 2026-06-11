import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteStaticCopy } from 'vite-plugin-static-copy'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const base = '/myweb/'

/** 开发环境直接读取本地 Music/（不复制 163MB 到 dist） */
function serveLocalMusic() {
  return {
    name: 'serve-local-music',
    configureServer(server) {
      server.middlewares.use(`${base}Music`, (req, res, next) => {
        const rel = decodeURIComponent(req.url || '/')
        const filePath = path.join(__dirname, 'Music', rel)
        if (!filePath.startsWith(path.join(__dirname, 'Music'))) {
          res.statusCode = 403
          res.end()
          return
        }
        fs.stat(filePath, (err, stat) => {
          if (err || !stat.isFile()) {
            next()
            return
          }
          const ext = path.extname(filePath).toLowerCase()
          const types = {
            '.mp3': 'audio/mpeg',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg',
            '.wav': 'audio/wav',
          }
          res.setHeader('Content-Type', types[ext] || 'application/octet-stream')
          fs.createReadStream(filePath).pipe(res)
        })
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  base,
  plugins: [
    vue(),
    serveLocalMusic(),
    viteStaticCopy({
      targets: [
        {
          src: 'Content',
          dest: ''
        },
        {
          src: 'img',
          dest: ''
        }
      ]
    })
  ],
  build: {
    outDir: 'docs'
  }
})