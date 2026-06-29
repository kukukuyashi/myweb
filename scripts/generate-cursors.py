#!/usr/bin/env python3
"""从 img/Mouse animation/ 的 PNG 序列生成 public/cursors/ 下的 64×64 动态光标 GIF。"""

from __future__ import annotations

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
SIZE = 64
FRAME_MS = 33  # ~30fps

# 优先使用 PNG 序列（帧数更多、画质更高）
MAPPING = {
    '普通（第二版）': 'normal.gif',
    '交互（第二版）': 'pointer.gif',
    '文本': 'text.gif',
    '加载': 'busy.gif',
}


def sort_key(path: Path) -> int:
    match = re.search(r'(\d+)\.png$', path.name, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def resize_png_sequence(src_dir: Path, dest: Path) -> None:
    pngs = sorted(src_dir.glob('*.png'), key=sort_key)
    if not pngs:
        raise RuntimeError(f'目录内无 PNG: {src_dir}')

    frames = [
        Image.open(p).convert('RGBA').resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        for p in pngs
    ]

    dest.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        dest,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=False,
    )
    print(f'{src_dir.name}/ → {dest.name}  ({len(frames)} 帧, {SIZE}×{SIZE})')


def main() -> None:
    if not SRC_DIR.is_dir():
        print(f'源目录不存在: {SRC_DIR}', file=sys.stderr)
        sys.exit(1)

    for folder_name, out_name in MAPPING.items():
        src = SRC_DIR / folder_name
        if not src.is_dir():
            print(f'缺少源目录: {src}', file=sys.stderr)
            sys.exit(1)
        resize_png_sequence(src, OUT_DIR / out_name)

    print('完成 →', OUT_DIR)


if __name__ == '__main__':
    main()
