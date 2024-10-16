#!/bin/bash

# Set output directory
OUTPUT_DIR="build"

# Main Python file to compile
MAIN_FILE="00_main.py"

# Compile with Nuitka
nuitka --standalone \
       --enable-plugin=tk-inter \
       --output-dir="$OUTPUT_DIR" \
       --include-data-files=Fault85.png=./Fault85.png \
       --include-data-files=Fault95.png=./Fault95.png \
       --include-data-files=Ficep_Logo.png=./Ficep_Logo.png \
       --include-data-files=StartupProcess.sh=./StartupProcess.sh \
       --include-data-files=Fault80.png=./Fault80.png \
       --include-data-files=Fault115.png=./Fault115.png \
       "$MAIN_FILE"

echo "Compilation finished. Output can be found in the $OUTPUT_DIR directory."
