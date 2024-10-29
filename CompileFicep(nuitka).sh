#!/bin/bash

# Set output directory
OUTPUT_DIR="build"

# Main Python file to compile
MAIN_FILE="00_main.py"


echo "Compilation finished. Output can be found in the $OUTPUT_DIR directory."

python3.8 -m nuitka --standalone \
       --enable-plugin=tk-inter \
       --output-dir="$OUTPUT_DIR" \
       --include-data-files=Fault50.png=./Fault50.png \
       --include-data-files=Fault51.png=./Fault51.png \
       --include-data-files=Ficep_Logo.png=./Ficep_Logo.png \
       --include-data-files=StartupProcess.sh=./StartupProcess.sh \
       --include-data-files=Fault52.png=./Fault52.png \
       --include-data-files=Fault53.png=./Fault53.png \
       --include-module=gi \
       "$MAIN_FILE"

echo "Compilation finished. Output can be found in the $OUTPUT_DIR directory."
