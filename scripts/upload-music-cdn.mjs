/**
 * 将本地 Music/ 上传到 S3 兼容对象存储（R2 / 阿里云 OSS S3 协议 / AWS S3）
 *
 * 用法：
 *   1. 在 .env.local 填写 CDN_S3_*（见 .env.example）
 *   2. npm run music:upload
 *
 * 上传后设置 VITE_MUSIC_BASE_URL 为桶的公开访问根地址（末尾不要 /）
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { S3Client } from '@aws-sdk/client-s3'
import { Upload } from '@aws-sdk/lib-storage'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const musicRoot = path.join(root, 'Music')

const AUDIO_RE = /\.(flac|mp3|ogg|wav)$/i

function loadEnvFile(relPath) {
  const file = path.join(root, relPath)
  if (!fs.existsSync(file)) return
  for (const line of fs.readFileSync(file, 'utf8').split('\n')) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue
    const eq = trimmed.indexOf('=')
    if (eq <= 0) continue
    const key = trimmed.slice(0, eq).trim()
    let val = trimmed.slice(eq + 1).trim()
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1)
    }
    if (!process.env[key]) process.env[key] = val
  }
}

function requireEnv(name) {
  const v = (process.env[name] || '').trim()
  if (!v) throw new Error(`缺少环境变量 ${name}（在 .env.local 中配置）`)
  return v
}

function walkAudio(dir, rel = '') {
  const files = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const relPath = rel ? `${rel}/${entry.name}` : entry.name
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      files.push(...walkAudio(full, relPath))
    } else if (AUDIO_RE.test(entry.name)) {
      files.push({ full, key: `Music/${relPath.replace(/\\/g, '/')}` })
    }
  }
  return files
}

loadEnvFile('.env.local')
loadEnvFile('.env')

const bucket = requireEnv('CDN_S3_BUCKET')
const accessKeyId = requireEnv('CDN_S3_ACCESS_KEY_ID')
const secretAccessKey = requireEnv('CDN_S3_SECRET_ACCESS_KEY')
const endpoint = (process.env.CDN_S3_ENDPOINT || '').trim()
const region = (process.env.CDN_S3_REGION || 'auto').trim()
const prefix = (process.env.CDN_S3_PREFIX || '').trim().replace(/^\/+|\/+$/g, '')
const forcePathStyle = process.env.CDN_S3_FORCE_PATH_STYLE === '1'

if (!fs.existsSync(musicRoot)) {
  console.error('Music/ 目录不存在')
  process.exit(1)
}

const client = new S3Client({
  region,
  endpoint: endpoint || undefined,
  credentials: { accessKeyId, secretAccessKey },
  forcePathStyle,
})

const files = walkAudio(musicRoot)
if (!files.length) {
  console.error('Music/ 下没有音频文件')
  process.exit(1)
}

console.log(`上传 ${files.length} 个文件 → s3://${bucket}/${prefix ? prefix + '/' : ''}Music/...`)

let ok = 0
for (const { full, key } of files) {
  const objectKey = prefix ? `${prefix}/${key}` : key
  const ext = path.extname(full).toLowerCase()
  const contentType =
    ext === '.mp3' ? 'audio/mpeg'
    : ext === '.flac' ? 'audio/flac'
    : ext === '.ogg' ? 'audio/ogg'
    : ext === '.wav' ? 'audio/wav'
    : 'application/octet-stream'

  process.stdout.write(`↑ ${objectKey} ... `)
  try {
    const upload = new Upload({
      client,
      params: {
        Bucket: bucket,
        Key: objectKey,
        Body: fs.createReadStream(full),
        ContentType: contentType,
      },
    })
    await upload.done()
    ok++
    console.log('OK')
  } catch (err) {
    console.log('FAIL')
    console.error(err.message || err)
    process.exit(1)
  }
}

console.log(`\n完成 ${ok}/${files.length}`)
const publicBase = (process.env.VITE_MUSIC_BASE_URL || '').trim()
if (publicBase) {
  console.log(`VITE_MUSIC_BASE_URL=${publicBase}`)
} else {
  console.log('请在 .env.local 设置 VITE_MUSIC_BASE_URL，并同步到 GitHub Actions 变量')
}
