import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const md = fs.readFileSync(path.join(__dirname, '../笔记/留言板 Twikoo 部署笔记.md'), 'utf8')

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function inline(s) {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}

const lines = md.split('\n')
const out = []
let inCode = false
let codeLang = ''
let inTable = false
let tableHeadDone = false

for (let i = 0; i < lines.length; i++) {
  const line = lines[i]

  if (line.startsWith('```')) {
    if (!inCode) {
      inCode = true
      codeLang = line.slice(3).trim()
      out.push('<pre><code>')
    } else {
      inCode = false
      out.push('</code></pre>')
    }
    continue
  }
  if (inCode) {
    out.push(esc(line))
    continue
  }

  if (line.startsWith('|') && line.includes('|')) {
    if (/^\|[\s\-:|]+\|$/.test(line.trim())) continue
    const cells = line.split('|').slice(1, -1).map(c => c.trim())
    if (!inTable) {
      inTable = true
      tableHeadDone = false
      out.push('<table><thead><tr>')
      cells.forEach(c => out.push(`<th>${inline(c)}</th>`))
      out.push('</tr></thead><tbody>')
      tableHeadDone = true
      continue
    }
    out.push('<tr>')
    cells.forEach(c => out.push(`<td>${inline(c)}</td>`))
    out.push('</tr>')
    continue
  } else if (inTable) {
    out.push('</tbody></table>')
    inTable = false
    tableHeadDone = false
  }

  if (line.startsWith('# ')) {
    out.push(`<h1>${inline(line.slice(2))}</h1>`)
  } else if (line.startsWith('## ')) {
    out.push(`<h2>${inline(line.slice(3))}</h2>`)
  } else if (line.startsWith('### ')) {
    out.push(`<h3>${inline(line.slice(4))}</h3>`)
  } else if (line.startsWith('> ')) {
    out.push(`<blockquote>${inline(line.slice(2))}</blockquote>`)
  } else if (line.startsWith('- ')) {
    out.push(`<ul><li>${inline(line.slice(2))}</li></ul>`)
  } else if (/^\d+\.\s/.test(line)) {
    out.push(`<ol><li>${inline(line.replace(/^\d+\.\s/, ''))}</li></ol>`)
  } else if (line.trim() === '---') {
    out.push('<hr>')
  } else if (line.trim() === '') {
    // skip
  } else {
    out.push(`<p>${inline(line)}</p>`)
  }
}

if (inTable) out.push('</tbody></table>')

const intro = '<p class="article-intro">Twikoo 留言板部署完整笔记：MongoDB Atlas + Netlify 云函数 + 博客前端接入，含踩坑与故障排查。</p>\n'
const html = intro + out.join('\n')
const dest = path.join(__dirname, '../Content/留言板 Twikoo 部署笔记.html')
fs.writeFileSync(dest, html, 'utf8')
console.log('Wrote', dest)
