"""
print_card.py - テキストファイルを枠画像と組み合わせて画像を生成するスクリプト

使用例:
    python print_card.py --txt message.txt --border border.png
    python print_card.py --txt message.txt --border border.png --output card.png
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# 53mm ロール紙 @ 203 DPI (8 dots/mm): 53 × 8 = 424px
DEFAULT_WIDTH = 424

CANDIDATE_FONTS = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]

LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.jpg"


def load_font(font_path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if font_path:
        return ImageFont.truetype(font_path, size)
    for path in CANDIDATE_FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int) -> list[str]:
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


def render_card(
    text: str,
    border_path: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    padding: int,
    width: int,
    line_spacing: int,
) -> Image.Image:
    # 背景タイルを作成（幅に合わせてリサイズ）
    tile = Image.open(border_path).convert("RGB")
    tile_h = int(width * tile.height / tile.width)
    tile = tile.resize((width, tile_h), Image.LANCZOS)

    # 行の高さを計算
    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    line_height = draw.textbbox((0, 0), "あAg", font=font)[3] + line_spacing

    # 角丸矩形の外側マージン
    rect_inset = 16
    text_area_width = width - rect_inset * 2 - padding * 2

    lines = wrap_text(text, font, text_area_width)
    text_height = line_height * len(lines)

    # ロゴの読み込みとリサイズ
    logo_img = None
    logo_section_height = 0
    logo_margin = line_height * 3 // 2
    if LOGO_PATH.exists():
        raw_logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_w = int(width * 0.25)
        logo_h = int(logo_w * raw_logo.height / raw_logo.width)
        logo_img = raw_logo.resize((logo_w, logo_h), Image.LANCZOS)
        logo_section_height = logo_margin + logo_h + logo_margin

    # キャンバスの高さを決定
    content_height = rect_inset + padding + text_height + logo_section_height + padding + rect_inset
    canvas_height = max(tile_h, content_height)

    # 背景タイルを縦に敷き詰める
    canvas = Image.new("RGB", (width, canvas_height), "white")
    for y_tile in range(0, canvas_height, tile_h):
        canvas.paste(tile, (0, y_tile))

    # 白い角丸矩形を描画
    draw = ImageDraw.Draw(canvas)
    rect_box = (rect_inset, rect_inset, width - rect_inset, canvas_height - rect_inset)
    draw.rounded_rectangle(rect_box, radius=20, fill="white")

    # テキストを描画
    x = rect_inset + padding
    y = rect_inset + padding
    for line in lines:
        draw.text((x, y), line, font=font, fill="black")
        y += line_height

    # ロゴを描画（テキスト後、左右中央）
    if logo_img:
        y += logo_margin
        logo_x = (width - logo_img.width) // 2
        canvas.paste(logo_img, (logo_x, y), logo_img)

    return canvas


def main():
    parser = argparse.ArgumentParser(description="テキストを枠画像に重ねて画像を生成します")
    parser.add_argument("--txt", default="message.txt", help="印刷するテキストファイル (デフォルト: message.txt)")
    parser.add_argument("--border", default="../assets/border.png", help="枠として使う画像ファイル (デフォルト: ../assets/border.png)")
    parser.add_argument("--output", default="output.png", help="出力ファイル名 (デフォルト: output.png)")
    parser.add_argument("--font", default=None, help="フォントファイルパス (.ttf/.ttc)")
    parser.add_argument("--font-size", type=int, default=16, help="フォントサイズ (デフォルト: 16)")
    parser.add_argument("--padding", type=int, default=32, help="角丸矩形内のマージン px (デフォルト: 32)")
    parser.add_argument("--line-spacing", type=int, default=6, help="行間 px (デフォルト: 6)")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help=f"画像幅 px (デフォルト: {DEFAULT_WIDTH})")
    args = parser.parse_args()

    txt_path = Path(args.txt)
    if not txt_path.exists():
        print(f"エラー: テキストファイルが見つかりません: {args.txt}", file=sys.stderr)
        sys.exit(1)

    border_path = Path(args.border)
    if not border_path.exists():
        print(f"エラー: 枠画像が見つかりません: {args.border}", file=sys.stderr)
        sys.exit(1)

    if not LOGO_PATH.exists():
        print(f"情報: ロゴ画像が見つかりません ({LOGO_PATH})。ロゴなしで生成します。")

    text = txt_path.read_text(encoding="utf-8")
    font = load_font(args.font, args.font_size)

    print(f"画像を生成中... (幅: {args.width}px, フォントサイズ: {args.font_size}px)")
    card = render_card(
        text=text,
        border_path=str(border_path),
        font=font,
        padding=args.padding,
        width=args.width,
        line_spacing=args.line_spacing,
    )

    card.save(args.output)
    print(f"保存完了: {args.output}")


if __name__ == "__main__":
    main()
