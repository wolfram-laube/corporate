#!/bin/bash
#
# Update Google Drive Links in all READMEs
#

DRIVE_URL="https://drive.google.com/drive/folders/0AHcy3s-c9X4AUk9PVA"

echo "🔗 Updating Google Drive links..."

find . -name "README.md" -exec sed -i '' "s|https://drive.google.com/\.\.\.|$DRIVE_URL|g" {} \;

echo "✅ Done!"
echo ""
grep -r "drive.google.com" . --include="*.md" | head -10
