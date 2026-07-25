#!/usr/bin/env python3
"""从 img/Mouse animation/ 的 PNG 序列生成光标资源（GIF + Canvas 用精灵图）。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print('需要 Pillow：pip install Pillow', file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / 'img' / 'Mouse animation'
OUT_DIR = ROOT / 'public' / 'cursors'
OUT_SIZE = 96
HOTSPOT = (12, 12)
CONTENT_FILL = 0.88
# 各光标单独填充比：文本是竖直 I-beam，长边=高，用 88% 会显得比其他光标高一截。
CONTENT_FILL_PER = {
    'text': 0.55,
}
FRAME_MS = 33
TRANSPARENT_INDEX = 255

MAPPING = {
    '普通（第二版）': 'normal',
    '交互（第二版）': 'pointer',
    '文本': 'text',
    '加载': 'busy',
}

# 各状态锚点对齐方式，保证视觉大小一致
CURSOR_ANCHORS = {
    'normal': 'tip',
    'pointer': 'tip',
    'text': 'center-top',
    'busy': 'center',
}


def sort_key(path: Path) -> int:
    match = re.search(r'(\d+)\.png$', path.name, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def clean_alpha(frame: Image.Image) -> Image.Image:
    rgba = frame.convert('RGBA')
    px = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 48:
                px[x, y] = (0, 0, 0, 0)
            elif a < 220 and r < 64 and g < 64 and b < 64:
                px[x, y] = (0, 0, 0, 0)
    return rgba


def anchor_hotspot(anchor: str, nw: int, nh: int) -> tuple[int, int]:
    hx, hy = HOTSPOT
    if anchor == 'tip':
        return hx, hy
    if anchor == 'center-top':
        return hx, hy + nh // 2
    if anchor == 'center':
        return OUT_SIZE // 2, OUT_SIZE // 2
    return hx, hy


def normalize_frame(img: Image.Image, anchor: str) -> Image.Image:
    """按内容 bbox 等比放大到统一占比，消除各状态画布尺寸差异。"""
    img = clean_alpha(img)
    bbox = img.getbbox()
    if not bbox:
        return Image.new('RGBA', (OUT_SIZE, OUT_SIZE), (0, 0, 0, 0))

    cropped = img.crop(bbox)
    cw, ch = cropped.size
    target = OUT_SIZE * CONTENT_FILL_PER.get(CURRENT_CURSOR_ID, CONTENT_FILL)
    scale = target / max(cw, ch)
    nw = max(1, round(cw * scale))
    nh = max(1, round(ch * scale))
    resized = cropped.resize((nw, nh), Image.Resampling.LANCZOS)

    canvas = Image.new('RGBA', (OUT_SIZE, OUT_SIZE), (0, 0, 0, 0))
    hx, hy = HOTSPOT

    if anchor == 'tip':
        px, py = hx, hy
    elif anchor == 'center-top':
        px = hx - nw // 2
        py = hy
    elif anchor == 'center':
        px = (OUT_SIZE - nw) // 2
        py = (OUT_SIZE - nh) // 2
    else:
        px, py = hx, hy

    canvas.paste(resized, (px, py), resized)
    return canvas


def rgba_to_palette(frame: Image.Image) -> Image.Image:
    rgba = clean_alpha(frame)
    alpha = rgba.getchannel('A')
    rgb = rgba.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=254)
    mask = alpha.point(lambda a: 255 if a <= 128 else 0)
    rgb.paste(TRANSPARENT_INDEX, mask)
    rgb.info['transparency'] = TRANSPARENT_INDEX
    return rgb


def load_rgba_frames(src_dir: Path, anchor: str) -> list[Image.Image]:
    pngs = sorted(src_dir.glob('*.png'), key=sort_key)
    if not pngs:
        raise RuntimeError(f'目录内无 PNG: {src_dir}')
    return [normalize_frame(Image.open(p), anchor) for p in pngs]


def save_gif(frames_rgba: list[Image.Image], dest: Path) -> None:
    frames_p = [rgba_to_palette(f) for f in frames_rgba]
    dest.parent.mkdir(parents=True, exist_ok=True)
    frames_p[0].save(
        dest,
        save_all=True,
        append_images=frames_p[1:],
        duration=FRAME_MS,
        loop=0,
        disposal=2,
        optimize=False,
        transparency=TRANSPARENT_INDEX,
    )


def save_sprite_sheet(frames_rgba: list[Image.Image], dest: Path) -> None:
    sheet = Image.new('RGBA', (OUT_SIZE * len(frames_rgba), OUT_SIZE))
    for i, frame in enumerate(frames_rgba):
        sheet.paste(frame, (i * OUT_SIZE, 0))
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest, optimize=True)


def main() -> None:
    if not SRC_DIR.is_dir():
        print(f'源目录不存在: {SRC_DIR}', file=sys.stderr)
        sys.exit(1)

    manifest = {
        'size': OUT_SIZE,
        'hotspotX': HOTSPOT[0],
        'hotspotY': HOTSPOT[1],
        'frameMs': FRAME_MS,
        'cursors': {},
    }

    for folder_name, cursor_id in MAPPING.items():
        src = SRC_DIR / folder_name
        if not src.is_dir():
            print(f'缺少源目录: {src}', file=sys.stderr)
            sys.exit(1)

        global CURRENT_CURSOR_ID
        CURRENT_CURSOR_ID = cursor_id
        anchor = CURSOR_ANCHORS[cursor_id]
        frames = load_rgba_frames(src, anchor)
        save_gif(frames, OUT_DIR / f'{cursor_id}.gif')
        sheet_name = f'{cursor_id}-sheet.png'
        save_sprite_sheet(frames, OUT_DIR / sheet_name)

        first_png = sorted(src.glob('*.png'), key=sort_key)[0]
        first_bbox = clean_alpha(Image.open(first_png)).getbbox()
        nh = round(OUT_SIZE * CONTENT_FILL)
        if first_bbox:
            cw, ch = first_bbox[2] - first_bbox[0], first_bbox[3] - first_bbox[1]
            target = OUT_SIZE * CONTENT_FILL_PER.get(CURRENT_CURSOR_ID, CONTENT_FILL)
            scale = target / max(cw, ch)
            nw, nh = max(1, round(cw * scale)), max(1, round(ch * scale))
            hs_x, hs_y = anchor_hotspot(anchor, nw, nh)
        else:
            hs_x, hs_y = anchor_hotspot(anchor, 0, nh)

        manifest['cursors'][cursor_id] = {
            'frames': len(frames),
            'sheet': sheet_name,
            'anchor': anchor,
            'hotspotX': hs_x,
            'hotspotY': hs_y,
            'contentHeight': nh,
        }
        print(f'{folder_name}/ → {cursor_id} ({anchor})  {len(frames)} 帧 @ {OUT_SIZE}px')

    (OUT_DIR / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    print('完成 →', OUT_DIR)


if __name__ == '__main__':
    main()
