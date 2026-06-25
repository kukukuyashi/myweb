import fs from 'fs'
import path from 'path'
import readline from 'readline'
import { fileURLToPath } from 'url'
import { COMMON_CATEGORIES, createNote, todayISO } from './lib/notes-store.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')

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

function parseTags(input) {
  return input
    .split(/[,，]/)
    .map((t) => t.trim())
    .filter(Boolean)
}

async function main() {
  const defaultDate = todayISO()
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })

  console.log('\n新建 Markdown 笔记 — 文件会保存到 笔记/{分类}/\n')
  console.log('也可在本地管理台创建：npm run dev → /myweb/admin\n')

  try {
    const title = await ask(rl, '标题')
    if (!title) {
      console.log('已取消：标题不能为空')
      return
    }

    const categoryHint = COMMON_CATEGORIES.join(' / ')
    const category = await ask(rl, `分类 (${categoryHint})`, '学习')

    const tagsInput = await ask(rl, '标签（逗号分隔）', category)
    let tags = parseTags(tagsInput)
    if (tags.length === 0) tags = [category]

    const excerpt = await ask(rl, '摘要', `${title} — 学习笔记。`)
    const date = await ask(rl, '日期 YYYY-MM-DD', defaultDate)
    const cover = await ask(rl, '封面图路径（留空跳过）', '')
    const draftAns = await ask(rl, '存草稿箱 _drafts? (y/N)', 'N')
    const asDraft = draftAns.toLowerCase() === 'y'

    const previewPath = asDraft ? `_drafts/${title}.md` : `${category}/${title}.md`
    console.log('\n── 预览 ──')
    console.log(`  文件: 笔记/${previewPath}`)
    console.log(`  分类/标签: ${category} · ${tags.join(', ')}`)
    console.log(`  摘要: ${excerpt}`)
    console.log('──────────\n')

    const ok = await askYesNo(rl, '确认创建', true)
    if (!ok) {
      console.log('已取消')
      return
    }

    const created = createNote(root, {
      title,
      category,
      tags,
      excerpt,
      date,
      cover,
      asDraft,
    })

    console.log('\n✓ 已创建:')
    console.log(`  笔记/${created.relPath}`)
    console.log('\n下一步:')
    console.log('  1. 编辑 Markdown 正文（或打开 /myweb/admin）')
    console.log(`  2. npm run publish:post -- "笔记/${created.relPath}"`)
    console.log('  3. npm run build && git push\n')
  } finally {
    rl.close()
  }
}

main().catch((err) => {
  console.error(err.message || err)
  process.exit(1)
})
