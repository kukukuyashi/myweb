import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const aboutDir = path.join(__dirname, '../img/关于')
const outFile = path.join(__dirname, '../src/data/aboutGallery.js')

const IMAGE_RE = /\.(jpe?g|jfif|png|gif|webp)$/i
const THUMB_RE = /\.thumb\.webp$/i

const files = fs.readdirSync(aboutDir)
  .filter(f => IMAGE_RE.test(f) && !THUMB_RE.test(f))
  .sort((a, b) => a.localeCompare(b, 'en'))

const gallery = files.map((file, i) => {
  const num = String(i + 1).padStart(2, '0')
  return {
    path: `img/关于/${file}`,
    label: num,
  }
})

const content = `/**
 * 自动生成 — 勿手改。运行: node scripts/generate-about-gallery.mjs
 * 扫描 img/关于/ 下的图片，供贴纸墙组件使用
 */
export const aboutGallery = ${JSON.stringify(gallery, null, 2).replace(/"([^"]+)":/g, '$1:').replace(/"/g, "'")}
`

// Fix JSON.stringify output to use unquoted keys properly - simpler approach:
const lines = gallery.map(item =>
  `  { path: '${item.path}', label: '${item.label}' },`
)

const finalContent = `/**
 * 自动生成 — 勿手改。运行: node scripts/generate-about-gallery.mjs
 * 扫描 img/关于/ 下的图片，供贴纸墙组件使用
 */
export const aboutGallery = [
${lines.join('\n')}
]
`

fs.writeFileSync(outFile, finalContent, 'utf8')
console.log(`Generated ${gallery.length} items → ${outFile}`)
