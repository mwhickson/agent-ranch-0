#!/usr/bin/env bash

# Default to "projects/newproject" if no argument is passed
TARGET_DIR="${1:-projects/newproject}"

echo "Initializing Agent-Ranch-0 workspace in: ${TARGET_DIR}"

mkdir -p "${TARGET_DIR}"/{logs,prompts,src,tests}

# Create default PROJECT_SPEC.md stub if it doesn't exist
if [ ! -f "${TARGET_DIR}/PROJECT_SPEC.md" ]; then
cat << 'EOF' > "${TARGET_DIR}/PROJECT_SPEC.md"
# Project Specification

## Configuration
<!-- AR0_CONFIG: API_URL=http://localhost:5001/v1/chat/completions -->

## Overview
Describe the project requirements and objectives here...

## Technical Stack
- Languages: Python
- Frameworks: None
EOF
fi

echo "Workspace initialized successfully."
