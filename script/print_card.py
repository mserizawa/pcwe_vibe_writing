"""
print_card.py - ショートショートJSONからサムネイル画像を生成するスクリプト

使用例:
    python print_card.py ../shorts/a1b2c3d4-e5f6-7890-abcd-ef1234567890.json
    python print_card.py a1b2c3d4-e5f6-7890-abcd-ef1234567890          # UUID だけでも可
    python print_card.py ../shorts --latest                              # 最新 JSON を使用
    python print_card.py ../shorts/uuid.json --output card.png
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

# 53mm ロール紙 @ 203 DPI (8 dots/mm): 53 × 8 = 424px
DEFAULT_WIDTH = 424

ASSETS_DIR = Path(__file__).parent.parent / "assets"
BORDER_PATH = ASSETS_DIR / "border.png"
VW_LOGO_PATH = ASSETS_DIR / "vw_logo.png"

COPYRIGHT = "© 2026 読んでみてはラジオ"
SHORTS_DIR = Path(__file__).parent.parent / "shorts"
DIST_DIR = Path(__file__).parent / "dist"

# GitHub Pages の公開 URL（リポジトリを変更した場合はここを更新）
PAGES_BASE_URL = "https://mserizawa.github.io/pcwe_vibe_writing/#"

STORY_MAX_CHARS = 300

CANDIDATE_FONTS = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]

CANDIDATE_BOLD_FONTS = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]


def load_font(font_path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if font_path:
        return ImageFont.truetype(font_path, size)
    for path in CANDIDATE_FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def load_bold_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in CANDIDATE_BOLD_FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_text(text: str, font, max_width: int) -> list[str]:
    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    lines = []
    for paragraph in text.splitlines():
        if not paragraph.strip():
            lines.append("")
            continue
        current_line = ""
        for char in paragraph:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width and current_line:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
    return lines


def truncate_story(story: str, max_chars: int = STORY_MAX_CHARS) -> str:
    if len(story) <= max_chars:
        return story
    return story[:max_chars].rstrip() + "…"


def format_created_at(created_at: str) -> str:
    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def find_latest_json(directory: Path) -> Path:
    jsons = list(directory.glob("*.json"))
    if not jsons:
        print(f"エラー: JSONファイルが見つかりません: {directory}", file=sys.stderr)
        sys.exit(1)
    return max(jsons, key=lambda p: json.loads(p.read_text(encoding="utf-8")).get("created_at", ""))


def make_qr(url: str, size: int) -> Image.Image:
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((size, size), Image.LANCZOS)


def render_card(
    title: str,
    story: str,
    qr_url: str,
    created_at_str: str,
    font_path: str | None,
    font_size: int,
    padding: int,
    width: int,
    line_spacing: int,
) -> Image.Image:
    rect_inset = 16
    text_area_width = width - rect_inset * 2 - padding * 2

    title_font = load_font(font_path, int(font_size * 1.35))
    body_font = load_font(font_path, font_size)
    cta_font = load_font(font_path, int(font_size * 0.85))
    ts_font = load_font(font_path, int(font_size * 0.7))

    def line_h(font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> int:
        dummy = Image.new("RGB", (1, 1))
        return ImageDraw.Draw(dummy).textbbox((0, 0), "あAg", font=font)[3] + line_spacing

    title_lh = line_h(title_font)
    body_lh = line_h(body_font)
    cta_lh = line_h(cta_font)
    ts_lh = line_h(ts_font)

    title_lines = wrap_text(title, title_font, text_area_width)
    body_lines = wrap_text(story, body_font, text_area_width)
    cta_lines = wrap_text("＼続きはウェブで／", cta_font, text_area_width)

    qr_size = int(width * 0.5 * 2 / 3)
    qr_img = make_qr(qr_url, qr_size)

    # カード上部ロゴ（背景の上）
    vw_logo_img = None
    vw_logo_h = 0
    if VW_LOGO_PATH.exists():
        raw_vw = Image.open(VW_LOGO_PATH).convert("RGBA")
        vw_logo_w = int(width * 0.65)
        vw_logo_h = int(vw_logo_w * raw_vw.height / raw_vw.width)
        vw_logo_img = raw_vw.resize((vw_logo_w, vw_logo_h), Image.LANCZOS)

    vw_logo_top = rect_inset
    vw_logo_gap = padding // 2
    card_top = vw_logo_top + vw_logo_h + vw_logo_gap

    card_content_h = (
        padding
        + title_lh * len(title_lines) + padding
        + body_lh * len(body_lines) + body_lh * 2
        + cta_lh * len(cta_lines) + padding // 2
        + qr_size + int(padding * 1.5)
        + padding // 2 + ts_lh + 6
        + rect_inset
    )

    copyright_font = load_bold_font(int(font_size * 0.9))
    copyright_pad = padding // 2
    copyright_lh = line_h(copyright_font)

    tile = Image.open(BORDER_PATH).convert("RGB")
    tile_h = int(width * tile.height / tile.width)
    tile = tile.resize((width, tile_h), Image.LANCZOS)

    card_canvas_h = max(tile_h, card_top + card_content_h)
    canvas_height = card_canvas_h + copyright_pad + copyright_lh + copyright_pad
    canvas = Image.new("RGB", (width, canvas_height), "white")
    for y_tile in range(0, canvas_height, tile_h):
        canvas.paste(tile, (0, y_tile))

    # カード上部ロゴを背景に合成
    if vw_logo_img:
        vw_x = (width - vw_logo_img.width) // 2
        canvas.paste(vw_logo_img, (vw_x, vw_logo_top), vw_logo_img)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (rect_inset, card_top, width - rect_inset, card_canvas_h - rect_inset),
        radius=20,
        fill="white",
    )

    x = rect_inset + padding
    y = card_top + padding

    for line in title_lines:
        draw.text((x, y), line, font=title_font, fill="#111111")
        y += title_lh
    y += padding

    for line in body_lines:
        draw.text((x, y), line, font=body_font, fill="#333333")
        y += body_lh
    y += body_lh * 2

    for line in cta_lines:
        draw.text((width // 2, y), line, font=cta_font, fill="#111111", anchor="mt")
        y += cta_lh
    y += padding // 2

    canvas.paste(qr_img, ((width - qr_size) // 2, y))
    y += qr_size + int(padding * 1.5)

    y += padding // 2
    draw.text((width - rect_inset - padding // 2, y), created_at_str, font=ts_font, fill="#111111", anchor="rt")

    # カード外・背景上のコピーライト
    copyright_y = card_canvas_h - rect_inset + copyright_pad
    draw.text((width // 2, copyright_y), COPYRIGHT, font=copyright_font, fill="white", anchor="mt")

    return canvas


def main():
    parser = argparse.ArgumentParser(description="ショートショートJSONからサムネイル画像を生成します")
    parser.add_argument("short", help="JSONファイルパス、UUID、またはディレクトリ（--latestと併用）")
    parser.add_argument("--latest", action="store_true", help="ディレクトリ内で created_at が最新の JSON を使用")
    parser.add_argument("--output", default=None, help="出力ファイル名（デフォルト: {uuid}.png）")
    parser.add_argument("--font", default=None, help="フォントファイルパス (.ttf/.ttc)")
    parser.add_argument("--font-size", type=int, default=16)
    parser.add_argument("--padding", type=int, default=32)
    parser.add_argument("--line-spacing", type=int, default=6)
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    args = parser.parse_args()

    short_path = Path(args.short)

    if args.latest:
        if not short_path.is_dir():
            print(f"エラー: --latest にはディレクトリを指定してください: {short_path}", file=sys.stderr)
            sys.exit(1)
        short_path = find_latest_json(short_path)
    elif not short_path.suffix:
        short_path = SHORTS_DIR / f"{args.short}.json"

    if not short_path.exists():
        print(f"エラー: ファイルが見つかりません: {short_path}", file=sys.stderr)
        sys.exit(1)

    uuid = short_path.stem
    DIST_DIR.mkdir(exist_ok=True)
    output_path = args.output or str(DIST_DIR / f"{uuid}.png")

    data = json.loads(short_path.read_text(encoding="utf-8"))
    title = data["title"]
    story = truncate_story(data["story"])
    created_at_str = format_created_at(data["created_at"])
    qr_url = f"{PAGES_BASE_URL}{uuid}"

    print(f"タイトル : {title}")
    print(f"作成日時 : {created_at_str}")
    print(f"QR URL  : {qr_url}")
    print("生成中...")

    card = render_card(
        title=title,
        story=story,
        qr_url=qr_url,
        created_at_str=created_at_str,
        font_path=args.font,
        font_size=args.font_size,
        padding=args.padding,
        width=args.width,
        line_spacing=args.line_spacing,
    )
    card.save(output_path)
    print(f"保存完了 : {output_path}")


if __name__ == "__main__":
    main()
