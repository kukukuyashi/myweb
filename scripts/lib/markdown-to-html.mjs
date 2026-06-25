function esc(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function inline(s) {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}

function flushList(out, type, items) {
  if (items.length === 0) return
  const tag = type === 'ol' ? 'ol' : 'ul'
  out.push(`<${tag}>`)
  for (const item of items) out.push(`<li>${inline(item)}</li>`)
  out.push(`</${tag}>`)
  items.length = 0
}

/** 将 Markdown 正文转为博客 Content HTML 片段 */
export function markdownToHtml(md) {
  const lines = md.replace(/^\uFEFF/, '').split('\n')
  const out = []
  let inCode = false
  let codeLang = ''
  let inTable = false
  let ulItems = []
  let olItems = []

  const closeLists = () => {
    flushList(out, 'ul', ulItems)
    flushList(out, 'ol', olItems)
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    if (line.startsWith('```')) {
      closeLists()
      if (!inCode) {
        inCode = true
        codeLang = line.slice(3).trim() || 'javascript'
        out.push(`<pre><code class="language-${esc(codeLang)}">`)
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
      closeLists()
      if (/^\|[\s\-:|]+\|$/.test(line.trim())) continue
      const cells = line.split('|').slice(1, -1).map((c) => c.trim())
      if (!inTable) {
        inTable = true
        out.push('<table><thead><tr>')
        cells.forEach((c) => out.push(`<th>${inline(c)}</th>`))
        out.push('</tr></thead><tbody>')
        continue
      }
      out.push('<tr>')
      cells.forEach((c) => out.push(`<td>${inline(c)}</td>`))
      out.push('</tr>')
      continue
    }
    if (inTable) {
      out.push('</tbody></table>')
      inTable = false
    }

    if (line.startsWith('# ')) {
      closeLists()
      out.push(`<h1>${inline(line.slice(2))}</h1>`)
    } else if (line.startsWith('## ')) {
      closeLists()
      out.push(`<h2>${inline(line.slice(3))}</h2>`)
    } else if (line.startsWith('### ')) {
      closeLists()
      out.push(`<h3>${inline(line.slice(4))}</h3>`)
    } else if (line.startsWith('#### ')) {
      closeLists()
      out.push(`<h4>${inline(line.slice(5))}</h4>`)
    } else if (line.startsWith('> ')) {
      closeLists()
      out.push(`<blockquote>${inline(line.slice(2))}</blockquote>`)
    } else if (line.startsWith('- ')) {
      flushList(out, 'ol', olItems)
      ulItems.push(line.slice(2))
    } else if (/^\d+\.\s/.test(line)) {
      flushList(out, 'ul', ulItems)
      olItems.push(line.replace(/^\d+\.\s/, ''))
    } else if (line.trim() === '---') {
      closeLists()
      out.push('<hr>')
    } else if (line.trim() === '') {
      closeLists()
    } else {
      closeLists()
      out.push(`<p>${inline(line)}</p>`)
    }
  }

  closeLists()
  if (inTable) out.push('</tbody></table>')
  if (inCode) out.push('</code></pre>')

  return out.join('\n')
}
