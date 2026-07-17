/**
 * 从 src/data/posts.js 导出 public/data/posts.json，供线上运行时热更新目录。
 * 构建流程：npm run build 会调用本脚本。
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath, pathToFileURL } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const postsMod = await import(`${pathToFileURL(path.join(root, 'src/data/posts.js')).href}?t=${Date.now()}`)
const outDir = path.join(root, 'public', 'data')
const outFile = path.join(outDir, 'posts.json')

fs.mkdirSync(outDir, { recursive: true })
const payload = {
  generatedAt: new Date().toISOString(),
  posts: postsMod.posts,
}
fs.writeFileSync(outFile, `${JSON.stringify(payload, null, 2)}\n`, 'utf8')
console.log(`[export-posts-json] ${postsMod.posts.length} posts → ${path.relative(root, outFile)}`)
