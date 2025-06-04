#!/bin/bash

# List of font URLs to download
FONT_URLS=(
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-LigIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-BolIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Bol.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Hai.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-HaiIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-LigIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Reg.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Bol.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Lig.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Bla.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Hai.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Reg.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Bla.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Lig.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-BlaIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-BlaIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-HaiIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-RegIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-BolIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-BolIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-Lig.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-Hai.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-Bla.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-BlaIta.woff"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-RegIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-RegIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-LigIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-Bol.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-LigIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-HaiIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-Reg.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-BolIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-HaiIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-LigIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-BlaIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-BolIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-HaiIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-BlaIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Bol.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Hai.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Reg.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Bol.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Lig.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Hai.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Reg.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Bla.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Bla.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Lig.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-BlaIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-BolIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-RegIta.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-Lig.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-Hai.ttf"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-Bla.ttf"
)

DOWNLOAD_DIR="downloaded_fonts"

# Create the download directory if it doesn't exist
mkdir -p "$DOWNLOAD_DIR"

echo "Starting font downloads to $DOWNLOAD_DIR..."

# Loop through each URL and attempt to download
for url in "${FONT_URLS[@]}"; do
  echo "Attempting to download: $url"
  
  # Use wget with --continue to resume partial downloads, --quiet for less output,
  # and --directory-prefix to save to a specific folder.
  # The '|| true' ensures the script doesn't exit on a non-zero exit code (like 404).
  wget --continue --quiet --directory-prefix="$DOWNLOAD_DIR" "$url" || {
    echo "  WARN: Failed to download $url (might be a 404 or other error, but continuing)."
  }
done

echo "All download attempts completed."
echo "Check the '$DOWNLOAD_DIR' directory for downloaded fonts."
exit 0