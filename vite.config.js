import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteStaticCopy } from 'vite-plugin-static-copy'
import fs from 'fs'
import path from 'path'
import { fileURLToPath, pathToFileURL } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const base = '/myweb/'
const adminPluginPath = path.join(__dirname, 'scripts/vite-notes-admin.mjs')

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
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
          }
          res.setHeader('Content-Type', types[ext] || 'application/octet-stream')
          fs.createReadStream(filePath).pipe(res)
        })
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig(async ({ mode, command }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const musicCdn = (env.VITE_MUSIC_BASE_URL || '').trim()
  const bundleMedia = env.VITE_BUNDLE_STATIC_MEDIA === '1'
  const staticTargets = [
    { src: 'Content', dest: '' },
  ]
  const musicDir = path.join(__dirname, 'Music')
  const imgDir = path.join(__dirname, 'img')

  if (bundleMedia || command === 'serve') {
    if (fs.existsSync(imgDir)) {
      staticTargets.push({ src: 'img', dest: '' })
    }
    if (!musicCdn && fs.existsSync(musicDir)) {
      staticTargets.push({ src: 'Music', dest: '' })
    }
  } else if (command === 'build') {
    console.log(
      '[vite] 生产构建不打包 img/Music（由 Nginx 同域提供）。GitHub Pages 请设 VITE_BUNDLE_STATIC_MEDIA=1'
    )
  }

  if (command === 'build' && !musicCdn && !bundleMedia && !fs.existsSync(musicDir)) {
    console.warn('[vite] Music/ 不在构建包内；线上需在 ECS 配置 /myweb/Music/ → /var/www/cyinc/Music/')
  }

  const plugins = [vue(), serveLocalImg(), serveLocalMusic()]

  if (command === 'serve' && fs.existsSync(adminPluginPath)) {
    const { notesAdminApi } = await import(
      /* @vite-ignore */ pathToFileURL(adminPluginPath).href
    )
    plugins.push(notesAdminApi(base))
  }

  plugins.push(viteStaticCopy({ targets: staticTargets }))

  return {
    base,
    plugins,
    build: {
      outDir: 'docs',
      target: 'es2020',
      cssCodeSplit: true,
      modulePreload: { polyfill: true },
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (
              id.includes('node_modules/vue/')
              || id.includes('node_modules/@vue/')
              || id.includes('node_modules/vue-router/')
              || id.includes('node_modules/pinia/')
            ) {
              return 'vue-vendor'
            }
            if (id.includes('node_modules/prismjs')) return 'prism'
            if (id.includes('node_modules/dompurify')) return 'dompurify'
          },
        },
      },
    },
  }
})
