"""Reverse-convert Content/*.html back to Markdown for the notes console.

Only the tags emitted by ``markdown_to_html`` are converted 1:1.  Anything the
converter does not understand (custom ``div``/``style``/``script``/``iframe`` ?)
is preserved verbatim as a raw HTML block so a later re-publish round-trips.
"""

from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from typing import Any

# Tags that map cleanly to Markdown constructs.
_BLOCK_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "blockquote", "pre", "hr",
    "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td",
}
_INLINE_TAGS = {"strong", "b", "em", "i", "code", "a", "img", "br"}
_KNOWN_TAGS = _BLOCK_TAGS | _INLINE_TAGS

# Blocks whose entire subtree we keep as raw HTML.
_RAW_TAGS = {"style", "script", "iframe", "svg", "video", "audio", "form", "figure"}


class _Node:
    __slots__ = ("tag", "attrs", "children", "parent", "raw")

    def __init__(self, tag: str, attrs: dict[str, str] | None = None, parent: "_Node | None" = None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children: list[Any] = []
        self.parent = parent
        self.raw: str | None = None


class _TreeBuilder(HTMLParser):
    """Builds a lightweight DOM tree; self-closing/void tags handled inline."""

    VOID = {"img", "br", "hr", "meta", "link", "input"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.root = _Node("__root__")
        self.stack = [self.root]
        self._raw_depth = 0
        self._raw_tag: str | None = None
        self._raw_buf: list[str] = []

    # -- raw passthrough (style/script/etc.) --
    def _start_raw(self, tag: str, attrs_html: str) -> None:
        self._raw_tag = tag
        self._raw_depth = 1
        self._raw_buf = [f"<{tag}{attrs_html}>"]

    def _attrs_to_html(self, attrs: list[tuple[str, str | None]]) -> str:
        out = ""
        for key, val in attrs:
            if val is None:
                out += f" {key}"
            else:
                out += f' {key}="{val}"'
        return out

    def handle_starttag(self, tag, attrs):
        attrs_html = self._attrs_to_html(attrs)
        if self._raw_tag is not None:
            if tag == self._raw_tag:
                self._raw_depth += 1
            self._raw_buf.append(f"<{tag}{attrs_html}>")
            return
        if tag in _RAW_TAGS:
            self._start_raw(tag, attrs_html)
            return
        node = _Node(tag, {k: (v or "") for k, v in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag in self.VOID:
            return
        self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        if self._raw_tag is not None:
            self._raw_buf.append(f"<{tag}{self._attrs_to_html(attrs)}/>")
            return
        node = _Node(tag, {k: (v or "") for k, v in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        if self._raw_tag is not None:
            self._raw_buf.append(f"</{tag}>")
            if tag == self._raw_tag:
                self._raw_depth -= 1
                if self._raw_depth <= 0:
                    raw_node = _Node("__raw__", parent=self.stack[-1])
                    raw_node.raw = "".join(self._raw_buf)
                    self.stack[-1].children.append(raw_node)
                    self._raw_tag = None
                    self._raw_buf = []
            return
        if tag in self.VOID:
            return
        for idx in range(len(self.stack) - 1, 0, -1):
            if self.stack[idx].tag == tag:
                del self.stack[idx:]
                return

    def handle_data(self, data):
        if self._raw_tag is not None:
            self._raw_buf.append(data)
            return
        if data:
            self.stack[-1].children.append(data)

    def handle_entityref(self, name):
        if self._raw_tag is not None:
            self._raw_buf.append(f"&{name};")
            return
        self.stack[-1].children.append(unescape(f"&{name};"))

    def handle_charref(self, name):
        if self._raw_tag is not None:
            self._raw_buf.append(f"&#{name};")
            return
        self.stack[-1].children.append(unescape(f"&#{name};"))


def _render_inline(node: _Node) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(re.sub(r"\s+", " ", child))
            continue
        if child.raw is not None:
            parts.append(child.raw)
            continue
        tag = child.tag
        if tag in ("strong", "b"):
            parts.append(f"**{_render_inline(child).strip()}**")
        elif tag in ("em", "i"):
            parts.append(f"*{_render_inline(child).strip()}*")
        elif tag == "code":
            parts.append(f"`{_text_only(child)}`")
        elif tag == "a":
            href = child.attrs.get("href", "")
            text = _render_inline(child).strip() or href
            parts.append(f"[{text}]({href})" if href else text)
        elif tag == "img":
            src = child.attrs.get("src", "")
            alt = child.attrs.get("alt", "")
            parts.append(f"![{alt}]({src})")
        elif tag == "br":
            parts.append("  \n")
        else:
            parts.append(_render_inline(child))
    return "".join(parts)


def _text_only(node: _Node) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif child.raw is not None:
            parts.append(child.raw)
        else:
            parts.append(_text_only(child))
    return "".join(parts)


def _render_block(node: _Node, out: list[str]) -> None:
    tag = node.tag

    if node.raw is not None:
        out.append(node.raw.strip())
        return

    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag[1])
        out.append(f"{'#' * level} {_render_inline(node).strip()}")
        return
    if tag == "p":
        text = _render_inline(node).strip()
        if text:
            out.append(text)
        return
    if tag == "blockquote":
        inner: list[str] = []
        _render_children(node, inner)
        quoted = [
            (f"> {chunk}" if chunk else ">")
            for chunk in "\n\n".join(inner).split("\n")
        ]
        out.append("\n".join(quoted))
        return
    if tag == "pre":
        code = node
        code_child = next((c for c in node.children if isinstance(c, _Node) and c.tag == "code"), None)
        lang = ""
        if code_child is not None:
            cls = code_child.attrs.get("class", "")
            m = re.search(r"language-([\w+-]+)", cls) or re.search(r"\b([\w+-]+)\b", cls)
            if m:
                lang = m.group(1)
            code = code_child
        body = _text_only(code)
        body = body.strip("\n")
        out.append(f"```{lang}\n{body}\n```")
        return
    if tag == "hr":
        out.append("---")
        return
    if tag == "ul":
        items = [
            f"- {_render_inline(li).strip()}"
            for li in node.children
            if isinstance(li, _Node) and li.tag == "li"
        ]
        if items:
            out.append("\n".join(items))
        return
    if tag == "ol":
        items = []
        idx = 1
        for li in node.children:
            if isinstance(li, _Node) and li.tag == "li":
                items.append(f"{idx}. {_render_inline(li).strip()}")
                idx += 1
        if items:
            out.append("\n".join(items))
        return
    if tag == "table":
        _render_table(node, out)
        return

    # Unknown container: recurse into children, unrecognized ones fall back to raw.
    if tag in ("div", "section", "article", "main", "span", "__root__"):
        _render_children(node, out)
        return

    # Anything else: keep the raw HTML of this node.
    out.append(_outer_html(node).strip())


def _render_children(node: _Node, out: list[str]) -> None:
    text_buf: list[str] = []

    def flush_text() -> None:
        joined = re.sub(r"\s+", " ", "".join(text_buf)).strip()
        if joined:
            out.append(joined)
        text_buf.clear()

    for child in node.children:
        if isinstance(child, str):
            text_buf.append(child)
            continue
        if child.raw is not None:
            flush_text()
            out.append(child.raw.strip())
            continue
        if child.tag in _BLOCK_TAGS or child.tag in ("div", "section", "article", "main"):
            flush_text()
            _render_block(child, out)
        else:
            text_buf.append(_render_inline_wrap(child))
    flush_text()


def _render_inline_wrap(node: _Node) -> str:
    wrapper = _Node("__wrap__")
    wrapper.children = [node]
    return _render_inline(wrapper)


def _render_table(node: _Node, out: list[str]) -> None:
    rows: list[list[str]] = []
    header: list[str] | None = None
    for section in _iter_rows(node):
        cells = []
        is_header = False
        for cell in section.children:
            if isinstance(cell, _Node) and cell.tag in ("th", "td"):
                cells.append(_render_inline(cell).strip().replace("|", "\\|"))
                if cell.tag == "th":
                    is_header = True
        if not cells:
            continue
        if is_header and header is None:
            header = cells
        else:
            rows.append(cells)
    if header is None and rows:
        header = rows.pop(0)
    if not header:
        return
    table_lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in rows:
        while len(row) < len(header):
            row.append("")
        table_lines.append("| " + " | ".join(row) + " |")
    out.append("\n".join(table_lines))


def _iter_rows(node: _Node):
    for child in node.children:
        if not isinstance(child, _Node):
            continue
        if child.tag == "tr":
            yield child
        elif child.tag in ("thead", "tbody", "tfoot"):
            for tr in child.children:
                if isinstance(tr, _Node) and tr.tag == "tr":
                    yield tr


def _outer_html(node: _Node) -> str:
    attrs = "".join(f' {k}="{v}"' for k, v in node.attrs.items())
    inner = "".join(
        c if isinstance(c, str) else (c.raw if c.raw is not None else _outer_html(c))
        for c in node.children
    )
    return f"<{node.tag}{attrs}>{inner}</{node.tag}>"


def _strip_publish_chrome(html: str) -> str:
    """Remove the intro/H1/date-blockquote/hr that build_article_html injects."""
    html = re.sub(r'<p class="article-intro">[\s\S]*?</p>', "", html, count=1, flags=re.I)
    date_word = "\u65e5\u671f"
    pattern = (
        r"^\s*<h1[^>]*>[\s\S]*?</h1>\s*"
        r"<blockquote>\s*" + date_word + r"[\uff1a:][\s\S]*?</blockquote>"
        r"\s*<hr\s*/?>"
    )
    html = re.sub(pattern, "", html, count=1, flags=re.I)
    return html


def html_to_markdown(html: str) -> str:
    html = _strip_publish_chrome(html or "")
    builder = _TreeBuilder()
    builder.feed(html)
    builder.close()
    out: list[str] = []
    _render_children(builder.root, out)
    blocks = [b.rstrip() for b in out if b and b.strip()]
    return "\n\n".join(blocks).strip() + "\n"
