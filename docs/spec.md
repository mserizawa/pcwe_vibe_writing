# アプリ仕様書

## 概要

AIが自動生成したショートショート（掌編小説）を閲覧するウェブアプリ。

---

## ディレクトリ構成

```
pcwe_vibe_writing/
├── assets/       # 画像素材（スクリプト・ウェブ共用）
├── docs/         # ドキュメント
├── script/       # 画像生成Pythonスクリプト
├── shorts/       # AI生成ショートショートJSON（スクリプト・ウェブ共用）
└── web/          # ウェブアプリ（React + TailwindCSS）
```

---

## データ仕様

### shorts ディレクトリ

- スクリプトとウェブアプリの両方から参照される共用ディレクトリ
- AIが定期的に小説を生成し、ファイルを追加していく
- ファイル名: `{uuid}.json`（例: `550e8400-e29b-41d4-a716-446655440000.json`）

### JSON フォーマット

```json
{
  "title": "小説のタイトル",
  "created_at": "2026-05-02T12:00:00Z",
  "story": "本文テキスト"
}
```

| フィールド   | 型     | 説明           |
|------------|--------|--------------|
| title      | string | 小説のタイトル  |
| created_at | string | 生成日時（ISO 8601） |
| story      | string | 本文テキスト   |

---

## 画像生成スクリプト仕様

### 概要

`script/print_card.py` — ショートショート JSON からサムネイル画像を生成するスクリプト。  
SNS シェアや印刷（53mm ロール紙）での配布を想定。

### 使い方

```bash
cd script
.venv/bin/python print_card.py <JSONパスまたはUUID>
.venv/bin/python print_card.py <ディレクトリ> --latest   # 最新 JSON を自動選択

# 例
.venv/bin/python print_card.py ../shorts/550e8400-....json
.venv/bin/python print_card.py 550e8400-e29b-41d4-a716-446655440000
.venv/bin/python print_card.py ../shorts --latest
```

- UUID のみ指定した場合、`../shorts/{uuid}.json` を自動で参照する
- `--latest` を指定するとディレクトリ内の `created_at` が最新の JSON を使用する
- 出力先: `script/dist/{uuid}.png`（ディレクトリは自動作成、バージョン管理対象外）

### 出力画像のレイアウト

1. **タイトル**（大きめフォント）
2. **本文**（先頭 300 字で截断、超過時は `…` を末尾に付与）
3. **「＼続きはウェブで／」**（中央寄せ、黒色）
4. **QR コード**（中央寄せ）— GitHub Pages の該当 URL に遷移
5. **ロゴ**（`assets/logo.jpg`、中央寄せ）
6. **作成日時**（右下、右揃え、小さめグレー）— `YYYY-MM-DD HH:MM:SS` 形式

背景: `assets/border.png` をタイル表示し、その上に白い角丸矩形を重ねる構成。

### QR コード URL

```
https://mserizawa.github.io/pcwe_vibe_writing/#{uuid}
```

`PAGES_BASE_URL` 定数（`print_card.py` 冒頭）を変更することで対応 URL を切り替え可能。

### セットアップ

```bash
cd script
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

依存ライブラリ: `pillow`, `qrcode[pil]`

---

## ウェブアプリ仕様

### 技術スタック

- React
- TailwindCSS
- 静的サイト（ビルド成果物をホスティング）

### ルーティング

| URL                  | 動作                                              |
|---------------------|--------------------------------------------------|
| `/{base}#{uuid}`    | 対応する `shorts/{uuid}.json` を読み込んで小説を表示 |
| `/{base}`（# なし） | エラーメッセージを表示                              |
| 存在しない uuid      | エラーメッセージを表示                              |

ハッシュルーティング（`#uuid`）を採用。GitHub Pages でサーバー設定不要。

### 表示内容

- タイトル（title）
- 生成日時（created_at）
- 本文（story）

---

## デプロイ

- 公開先: GitHub Pages
- ブランチ運用:
  - `main` — ソースコード管理
  - `gh-pages` — ビルド成果物のデプロイ先（`web/` のビルド結果 + `shorts/` の JSON ファイルを配置）

### デプロイフロー

- `web/` のビルドと `shorts/` の更新は手動で `gh-pages` ブランチに反映する
- 小説を追加するたびに `gh-pages` ブランチの `shorts/` を更新してプッシュする
