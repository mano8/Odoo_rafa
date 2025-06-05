#!/bin/bash

# List of font URLs to download (as provided by user)
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
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-Hai.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Hai.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-Hai.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-HaiIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-HaiIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-HaiIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSans-LigIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-LigIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-LigIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-RegIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-RegIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-BolIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-BolIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-Bla.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansHebrew-BlaIta.woff2"
  "https://fonts.odoocdn.com/fonts/noto/NotoSansArabic-BlaIta.woff2"
)

DOWNLOAD_DIR="downloaded_fonts"
GOOGLE_FONTS_URL="https://fonts.google.com"

# Create the download directory if it doesn't exist
mkdir -p "$DOWNLOAD_DIR"

echo "Starting font downloads to $DOWNLOAD_DIR..."

# Loop through each URL and attempt to download
for url in "${FONT_URLS[@]}"; do
  echo "Attempting to download: $url"
  
  # Extract filename for user messages and potential saving
  filename=$(basename "$url")

  # Use wget with --continue to resume partial downloads, --quiet for less output,
  # --timeout and --tries for robustness, and --directory-prefix.
  # The '||' block is executed if wget returns a non-zero exit code (e.g., 404).
  wget --continue --quiet --timeout=15 --tries=2 --directory-prefix="$DOWNLOAD_DIR" "$url" || {
    # Check if the failed URL is from odoocdn
    if [[ "$url" == *"fonts.odoocdn.com"* ]]; then
      # Suggestion for Google Fonts
      font_name_suggestion="${filename%.*}" # Removes extension, e.g., NotoSansHebrew-BolIta
      
      # Basic parsing for a more user-friendly suggestion (can be expanded)
      # Example: NotoSansHebrew-BolIta -> Noto Sans Hebrew Bold Italic
      parsed_suggestion="$font_name_suggestion"
      parsed_suggestion="${parsed_suggestion/NotoSansArabic/Noto Sans Arabic}"
      parsed_suggestion="${parsed_suggestion/NotoSansHebrew/Noto Sans Hebrew}"
      parsed_suggestion="${parsed_suggestion/NotoSans/Noto Sans}"
      # Weights
      parsed_suggestion="${parsed_suggestion/-Reg/ Regular}"
      parsed_suggestion="${parsed_suggestion/-Bol/ Bold}"
      parsed_suggestion="${parsed_suggestion/-Lig/ Light}"
      parsed_suggestion="${parsed_suggestion/-Bla/ Black}"
      parsed_suggestion="${parsed_suggestion/-Hai/ Hairline}"
      # Styles
      parsed_suggestion="${parsed_suggestion/Ita/ Italic}"
      # Clean up potential double spaces from replacements
      parsed_suggestion=$(echo "$parsed_suggestion" | tr -s ' ')


      echo "  WARN: Failed to download $url from odoocdn."
      echo "  INFO: Please try to find a font matching '$parsed_suggestion' (based on filename '$filename')"
      echo "        from $GOOGLE_FONTS_URL."
      echo "        Download the .woff2 (recommended) or original format and place it in '$DOWNLOAD_DIR' as '$filename'."
    else
      # Generic warning for non-odoocdn URLs, if any were in the list
      echo "  WARN: Failed to download $url (might be a 404 or other error, but continuing)."
    fi
  }
done

echo ""
echo "All download attempts completed."
echo "Check the '$DOWNLOAD_DIR' directory for downloaded fonts and any warnings above for manual fallbacks."
exit 0