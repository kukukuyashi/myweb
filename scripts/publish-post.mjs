import readline from 'readline'
import path from 'path'
import { fileURLToPath } from 'url'
import {
  COMMON_CATEGORIES,
  resolveNotePath,
  todayISO,
  listNotes,
} from './lib/notes-store.mjs'
import {
  parseFrontmatter,
  publishMarkdownFile,
  resolvePostMeta,
} from './lib/post-publish.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const notesDir = path.join(root, '笔记')

function ask(rl, question, defaultValue = '') {
  const hint = defaultValue ? ` [${defaultValue}]` : ''
  return new Promise((resolve) => {
    rl.question(`${question}${hint}: `, (answer) => {
      resolve(answer.trim() || defaultValue)
    })
  })
}

function askYesNo(rl, question, defaultYes = true) {
  const hint = defaultYes ? ' [Y/n]' : ' [y/N]'
  return new Promise((resolve) => {
    rl.question(`${question}${hint}: `, (answer) => {
      const a = answer.trim().toLowerCase()
      if (!a) resolve(defaultYes)
      else resolve(a === 'y' || a === 'yes')
    })
  })
}

async function pickMarkdownFile(rl) {
  const files = listNotes(root).map((n) => n.relPath)
  if (files.length === 0) {
    console.log('\n笔记/ 目录下没有 .md 文件。先运行 npm run new:post 或在 /myweb/admin 创建。\n')
    return null
  }

  console.log('\n选择要发布的 Markdown：\n')
  files.forEach((file, i) => {
    console.log(`  ${i + 1}. ${file}`)
  })
  console.log('')

  const pick = await ask(rl, `序号 1-${files.length}`)
  const idx = Number(pick) - 1
  if (!Number.isInteger(idx) || idx < 0 || idx >= files.length) {
    console.log('无效序号')
    return null
  }
  return path.join(notesDir, files[idx])
}

async function fillMissingMeta(rl, mdPath, posts) {
  const raw = await import('fs').then((fs) => fs.readFileSync(mdPath, 'utf8'))
  const { meta, body } = parseFrontmatter(raw)
  const draft = resolvePostMeta({ meta, body, mdPath, posts })

  const needs = []
  if (!meta.title && !body.match(/^#\s+/m)) needs.push('title')
  if (!meta.excerpt) needs.push('excerpt')

  if (needs.length === 0) return {}

  console.log('\nFrontmatter 不完整，补充几项（回车用默认值）：\n')
  const defaults = {}

  if (needs.includes('title')) {
    defaults.title = await ask(rl, '标题', draft.title)
  }
  if (!meta.category) {
    const categoryHint = COMMON_CATEGORIES.join(' / ')
    defaults.category = await ask(rl, `分类 (${categoryHint})`, draft.category)
  }
  if (!meta.tags) {
    defaults.tags = await ask(rl, '标签（逗号分隔）', defaults.category || draft.category)
  }
  if (needs.includes('excerpt')) {
    defaults.excerpt = await ask(rl, '摘要', draft.excerpt)
  }
  if (!meta.date) {
    defaults.date = await ask(rl, '日期 YYYY-MM-DD', draft.date || todayISO())
  }

  return defaults
}

async function publishOne(mdPath, rl, posts, interactive) {
  const defaults = interactive ? await fillMissingMeta(rl, mdPath, posts) : {}
  const fs = await import('fs')
  const parsed = parseFrontmatter(fs.readFileSync(mdPath, 'utf8'))
  const preview = resolvePostMeta({
    meta: parsed.meta,
    body: parsed.body,
    mdPath,
    posts,
    defaults,
  })

  console.log('\n── 发布预览 ──')
  console.log(`  源文件:   ${path.relative(root, mdPath)}`)
  console.log(`  输出:     Content/${preview.file}`)
  console.log(`  id:       ${preview.id}${posts.some((p) => p.file === preview.file) ? '（更新已有文章）' : '（新建）'}`)
  console.log(`  标题:     ${preview.title}`)
  console.log(`  分类/标签: ${preview.category} · ${preview.tags.join(', ')}`)
  console.log(`  摘要:     ${preview.excerpt}`)
  console.log('──────────────\n')

  if (interactive) {
    const ok = await askYesNo(rl, '确认发布', true)
    if (!ok) {
      console.log('已取消')
      return false
    }
  }

  const result = publishMarkdownFile(mdPath, { root, posts, defaults })
  console.log('\n✓ 已发布:')
  console.log(`  Content/${result.post.file}`)
  console.log(`  src/data/posts.js（id ${result.post.id}${result.updated ? ' 已更新' : ' 已新增'}）`)
  console.log('\n下一步: npm run build && git push\n')
  return true
}

async function main() {
  const args = process.argv.slice(2)
  const all = args.includes('--all')
  const yes = args.includes('--yes') || args.includes('-y')
  const fileArgs = args.filter((a) => !a.startsWith('-'))

  const { posts } = await import('../src/data/posts.js')
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
  const interactive = !yes && process.stdin.isTTY

  try {
    if (all) {
      const files = listNotes(root).map((n) => path.join(notesDir, n.relPath))
      if (files.length === 0) {
        console.log('\n笔记/ 下没有 .md 文件\n')
        return
      }
      for (const file of files) {
        await publishOne(file, rl, posts, false)
      }
      return
    }

    let mdPath = fileArgs[0] ? resolveNotePath(root, fileArgs[0])?.absPath : null
    if (!mdPath && interactive) mdPath = await pickMarkdownFile(rl)
    if (!mdPath && fileArgs[0]) {
      console.error(`\n找不到 Markdown 文件: ${fileArgs[0]}\n`)
      process.exit(1)
    }
    if (!mdPath) {
      console.log('\n用法:')
      console.log('  npm run publish:post -- 笔记/部署/xxx.md')
      console.log('  npm run publish:post')
      console.log('  npm run publish:post -- --all --yes')
      console.log('  本地管理台: npm run dev → http://localhost:5173/myweb/admin\n')
      return
    }

    await publishOne(mdPath, rl, posts, interactive)
  } finally {
    rl.close()
  }
}

main().catch((err) => {
  console.error(err.message || err)
  process.exit(1)
})
