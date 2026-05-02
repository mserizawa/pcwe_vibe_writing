#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# git remote から repo 名と GitHub ユーザー名を取得
REMOTE_URL=$(git -C "$REPO_ROOT" remote get-url origin 2>/dev/null || true)
if [ -z "$REMOTE_URL" ]; then
  echo "エラー: git remote 'origin' が未設定です" >&2
  exit 1
fi
REPO_NAME=$(basename "$REMOTE_URL" .git)
GITHUB_USER=$(echo "$REMOTE_URL" | sed -E 's|.*[:/]([^/]+)/[^/]+\.git$|\1|')
BASE_PATH="/${REPO_NAME}/"

echo "→ ベースURL: $BASE_PATH"

# ウェブアプリをビルド
echo "→ ウェブアプリをビルド中..."
cd "$REPO_ROOT/web"
npm run build -- --base="$BASE_PATH"
cd "$REPO_ROOT"

# デプロイ用の一時ディレクトリを作成
DEPLOY_DIR=$(mktemp -d)
trap 'rm -rf "$DEPLOY_DIR"' EXIT

cp -r web/dist/. "$DEPLOY_DIR/"
cp -r assets/ "$DEPLOY_DIR/assets/"
if [ -d shorts ] && [ -n "$(ls -A shorts 2>/dev/null)" ]; then
  cp -r shorts/ "$DEPLOY_DIR/shorts/"
fi

# gh-pages ブランチへ強制プッシュ
echo "→ gh-pages へデプロイ中..."
cd "$DEPLOY_DIR"
git init -q
git checkout -b gh-pages
git add -A
git commit -q -m "deploy: $(date '+%Y-%m-%d %H:%M')"
git remote add origin "$REMOTE_URL"
git push -f origin gh-pages

echo ""
echo "デプロイ完了!"
echo "  https://${GITHUB_USER}.github.io/${REPO_NAME}/"
echo ""
echo "初回の場合は GitHub リポジトリの Settings → Pages で"
echo "  Source: Deploy from a branch"
echo "  Branch: gh-pages / (root)"
echo "に設定してください。"
