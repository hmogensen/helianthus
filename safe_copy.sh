#!/bin/bash

# Script to copy files without overwriting existing files
# Usage: ./safe_copy.sh <source_directory> <target_directory>

if [ $# -ne 2 ]; then
    echo "Usage: $0 <source_directory> <target_directory>"
    exit 1
fi

SOURCE_DIR="$1"
TARGET_DIR="$2"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist."
    exit 1
fi

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy files without overwriting (using -n flag)
echo "Copying files from '$SOURCE_DIR' to '$TARGET_DIR'..."
cp -rn "$SOURCE_DIR"/* "$TARGET_DIR"/ 2>/dev/null

echo "Copy operation completed. Existing files were preserved."

# Optional: Show which files were skipped
echo "Files that already existed and were skipped:"
for file in "$SOURCE_DIR"/*; do
    filename=$(basename "$file")
    if [ -e "$TARGET_DIR/$filename" ]; then
        echo "  - $filename"
    fi
done
