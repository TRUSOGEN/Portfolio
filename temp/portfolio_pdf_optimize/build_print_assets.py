"""生成作品集 PDF 专用素材并同步 print.html 的图片引用。

这个脚本只处理打印版依赖的图片，不修改原始高清素材。流程是：
1. 从 print.html 读取所有 img src 引用；
2. 将引用图片转成适合 A4 打印的 JPEG；
3. 把 print.html 中的 src 机械替换为 assets/print-pdf 下的轻量图片。
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path("/Users/trusoegn/resume/portfolio")
HTML_PATH = ROOT / "print.html"
OUT_DIR = ROOT / "assets" / "print-pdf"
MAX_EDGE = 1800
QUALITY = 82


def image_refs(html: str) -> list[str]:
    """按出现顺序提取 HTML 中的图片引用。"""

    refs = re.findall(r'src="([^"]+)"', html)
    return list(dict.fromkeys(refs))


def output_name(src: str) -> str:
    """为优化后的图片生成稳定文件名。"""

    path = Path(src)
    return f"{path.stem}.jpg"


def optimise_image(src: Path, dst: Path) -> tuple[int, int, int, int]:
    """将单张图片压缩为 PDF 友好的 sRGB JPEG。"""

    original_size = src.stat().st_size
    with Image.open(src) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
        dst.parent.mkdir(parents=True, exist_ok=True)
        image.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        width, height = image.size
    return original_size, dst.stat().st_size, width, height


def main() -> None:
    """执行素材生成和 HTML 引用替换。"""

    html = HTML_PATH.read_text(encoding="utf-8")
    refs = image_refs(html)
    total_original = 0
    total_optimised = 0

    for ref in refs:
        src = ROOT / ref
        if not src.exists():
            raise FileNotFoundError(src)
        dst_ref = f"assets/print-pdf/{output_name(ref)}"
        dst = ROOT / dst_ref
        original_size, optimised_size, width, height = optimise_image(src, dst)
        total_original += original_size
        total_optimised += optimised_size
        html = html.replace(f'src="{ref}"', f'src="{dst_ref}"')
        print(
            f"{ref} -> {dst_ref} "
            f"{original_size / 1024:.0f}KB -> {optimised_size / 1024:.0f}KB "
            f"({width}x{height})"
        )

    HTML_PATH.write_text(html, encoding="utf-8")
    print(
        f"total {total_original / 1024 / 1024:.2f}MB -> "
        f"{total_optimised / 1024 / 1024:.2f}MB, refs={len(refs)}"
    )


if __name__ == "__main__":
    main()
