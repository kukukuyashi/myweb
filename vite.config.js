import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteStaticCopy } from 'vite-plugin-static-copy'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const base = '/myweb/'

/** 开发环境直接读取本地 img/（含子目录） */
function serveLocalImg() {
  const imgRoot = path.join(__dirname, 'img')
  const types = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.jfif': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.ico': 'image/x-icon',
  }
  return {
    name: 'serve-local-img',
    configureServer(server) {
      server.middlewares.use(`${base}img`, (req, res, next) => {
        const rel = decodeURIComponent((req.url || '/').split('?')[0]).replace(/^\/+/, '')
        const filePath = path.normalize(path.join(imgRoot, rel))
        if (!filePath.startsWith(imgRoot)) {
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
          res.setHeader('Content-Type', types[ext] || 'application/octet-stream')
          fs.createReadStream(filePath).pipe(res)
        })
      })
    },
  }
}

/** 开发环境直接读取本地 Music/（不复制到 dist） */
function serveLocalMusic() {
  return {
    name: 'serve-local-music',
    configureServer(server) {
      server.middlewares.use(`${base}Music`, (req, res, next) => {
        const rel = decodeURIComponent((req.url || '/').split('?')[0]).replace(/^\/+/, '')
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
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const musicCdn = (env.VITE_MUSIC_BASE_URL || '').trim()
  const staticTargets = [
    { src: 'Content', dest: '' },
    { src: 'img', dest: '' },
  ]
  const musicDir = path.join(__dirname, 'Music')
  if (!musicCdn && fs.existsSync(musicDir)) {
    staticTargets.push({ src: 'Music', dest: '' })
  } else if (!musicCdn) {
    console.warn(
      '[vite] Music/ 不存在且未设置 VITE_MUSIC_BASE_URL，构建产物不含音频（线上需配置 CDN）'
    )
  }

  return {
    base,
    plugins: [
      vue(),
      serveLocalImg(),
      serveLocalMusic(),
      viteStaticCopy({ targets: staticTargets }),
    ],
    build: {
      outDir: 'docs',
    },
  }
})
