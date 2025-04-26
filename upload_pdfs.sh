#!/bin/bash
# Script to upload multiple PDF files in parallel to Yojna Khojna backend

# Default settings
BACKEND_URL="http://localhost:8000"
MAX_PARALLEL=5
PDF_DIR=""
PATTERN="*.pdf"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --url)
      BACKEND_URL="$2"
      shift 2
      ;;
    --max-parallel)
      MAX_PARALLEL="$2"
      shift 2
      ;;
    --pattern)
      PATTERN="$2"
      shift 2
      ;;
    *)
      if [[ -z "$PDF_DIR" ]]; then
        PDF_DIR="$1"
      else
        echo "Unknown argument: $1"
        exit 1
      fi
      shift
      ;;
  esac
done

# Check if directory is provided
if [[ -z "$PDF_DIR" ]]; then
  echo "Usage: $0 [--url BACKEND_URL] [--max-parallel NUM] [--pattern GLOB] PDF_DIRECTORY"
  exit 1
fi

# Check if directory exists
if [[ ! -d "$PDF_DIR" ]]; then
  echo "Error: $PDF_DIR is not a valid directory"
  exit 1
fi

# Find all PDF files matching the pattern
mapfile -t PDF_FILES < <(find "$PDF_DIR" -type f -name "$PATTERN" | sort)

# Check if any PDFs were found
if [[ ${#PDF_FILES[@]} -eq 0 ]]; then
  echo "No PDF files found in $PDF_DIR matching pattern $PATTERN"
  exit 1
fi

# Print found PDFs
echo "Found ${#PDF_FILES[@]} PDF files to upload:"
for i in "${!PDF_FILES[@]}"; do
  filename=$(basename "${PDF_FILES[$i]}")
  echo "  $((i+1)). $filename"
done

# Ask for confirmation
read -p "Upload ${#PDF_FILES[@]} PDFs to $BACKEND_URL? [y/N] " response
if [[ ! "$response" =~ ^[yY](es)?$ ]]; then
  echo "Upload canceled"
  exit 0
fi

# Function to upload a single PDF
upload_pdf() {
  local pdf_path="$1"
  local filename=$(basename "$pdf_path")
  
  echo "Uploading $filename..."
  response=$(curl -s -w "%{http_code}" -X POST "$BACKEND_URL/process-pdf" \
    -F "pdf_file=@$pdf_path" -o /tmp/output_${filename//[^a-zA-Z0-9]/_}.json)
  
  status_code=${response: -3}
  if [[ "$status_code" == "200" || "$status_code" == "202" ]]; then
    api_response=$(cat /tmp/output_${filename//[^a-zA-Z0-9]/_}.json)
    status=$(echo "$api_response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    echo "Successfully processed $filename: $status"
    echo "$filename: success ($status)" >> /tmp/upload_results.txt
  else
    echo "Error uploading $filename: HTTP $status_code"
    echo "$filename: error (HTTP $status_code)" >> /tmp/upload_results.txt
  fi
  
  rm -f /tmp/output_${filename//[^a-zA-Z0-9]/_}.json
}

# Set up for parallel uploads
export -f upload_pdf
export BACKEND_URL

# Clean up previous results
rm -f /tmp/upload_results.txt
touch /tmp/upload_results.txt

# Upload PDFs in parallel with limiting concurrency
echo -e "\nUploading files..."
printf "%s\n" "${PDF_FILES[@]}" | xargs -P "$MAX_PARALLEL" -I{} bash -c 'upload_pdf "$@"' _ {}

# Print summary
total=${#PDF_FILES[@]}
successful=$(grep -c "success" /tmp/upload_results.txt)
failed=$((total - successful))

echo -e "\nUpload Summary:"
echo "  Total: $total"
echo "  Successful: $successful"
echo "  Failed: $failed"

if [[ $failed -gt 0 ]]; then
  echo -e "\nFailed uploads:"
  grep "error" /tmp/upload_results.txt
fi

# Clean up
rm -f /tmp/upload_results.txt

echo -e "\nDone!" 