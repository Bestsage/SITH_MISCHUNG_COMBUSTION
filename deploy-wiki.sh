#!/bin/bash
# Deploy wiki to GitHub Wiki

set -e

REPO_NAME="SITH_MISCHUNG_COMBUSTION"
REPO_OWNER="Bestsage"
WIKI_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}.wiki.git"
WIKI_DIR="/tmp/wiki-deploy"

echo "🚀 Deploying Wiki to GitHub..."

# Clean up previous deployment directory
if [ -d "$WIKI_DIR" ]; then
    rm -rf "$WIKI_DIR"
fi

# Clone the wiki repository
echo "📥 Cloning wiki repository..."
git clone "$WIKI_URL" "$WIKI_DIR"

# Copy markdown files
echo "📝 Copying markdown files..."
cp wiki/*.md "$WIKI_DIR/"

# Navigate to wiki directory
cd "$WIKI_DIR"

# Check if there are changes
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ No changes to deploy."
    exit 0
fi

# Commit and push
echo "💾 Committing changes..."
git add .
git commit -m "Update wiki documentation with improved formatting

- Better visual structure with Markdown formatting
- Enhanced navigation between pages
- Improved content organization
- Better readability with tables, lists, and code blocks"

echo "📤 Pushing to GitHub Wiki..."
git push origin master

echo "✅ Wiki deployed successfully!"
echo "🔗 View at: https://github.com/${REPO_OWNER}/${REPO_NAME}/wiki"

# Clean up
cd -
rm -rf "$WIKI_DIR"
