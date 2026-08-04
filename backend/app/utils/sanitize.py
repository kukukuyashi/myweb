"""XSS 防护：使用 bleach 对用户内容做 HTML 白名单过滤。

只允许 Markdown 渲染常见的安全标签和属性，剥离 <script> / <iframe> / 事件属性等。
"""

import bleach

ALLOWED_TAGS = {
    "a", "abbr", "acronym", "b", "blockquote", "br", "code", "del",
    "div", "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr",
    "i", "img", "ins", "li", "ol", "p", "pre", "s", "span",
    "strong", "sub", "sup", "table", "tbody", "td", "th", "thead",
    "tr", "u", "ul",
}

ALLOWED_ATTRS = {
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
    "abbr": ["title"],
    "acronym": ["title"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(text: str) -> str:
    """过滤用户提交的 HTML / Markdown 内容，移除危险标签和属性。"""
    if not text:
        return text
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )