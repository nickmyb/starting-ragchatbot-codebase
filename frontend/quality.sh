#!/bin/bash
# Frontend Code Quality Check Script
# Run this script to check and fix code formatting and linting issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Frontend Code Quality Checks${NC}"
echo "=============================="
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
    echo ""
fi

# Parse arguments
FIX_MODE=false
CHECK_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX_MODE=true
            shift
            ;;
        --check)
            CHECK_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./quality.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --fix     Auto-fix formatting and linting issues"
            echo "  --check   Only check, don't fix (default)"
            echo "  -h        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Run checks
if [ "$FIX_MODE" = true ]; then
    echo -e "${YELLOW}Running Prettier (auto-fix)...${NC}"
    npm run format
    echo ""

    echo -e "${YELLOW}Running ESLint (auto-fix)...${NC}"
    npm run lint:fix
    echo ""

    echo -e "${GREEN}Code quality fixes applied!${NC}"
else
    EXIT_CODE=0

    echo -e "${YELLOW}Checking code formatting with Prettier...${NC}"
    if npm run format:check; then
        echo -e "${GREEN}Formatting check passed!${NC}"
    else
        echo -e "${RED}Formatting issues found. Run with --fix to auto-fix.${NC}"
        EXIT_CODE=1
    fi
    echo ""

    echo -e "${YELLOW}Checking code with ESLint...${NC}"
    if npm run lint; then
        echo -e "${GREEN}Linting check passed!${NC}"
    else
        echo -e "${RED}Linting issues found. Run with --fix to auto-fix.${NC}"
        EXIT_CODE=1
    fi
    echo ""

    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}All quality checks passed!${NC}"
    else
        echo -e "${RED}Some quality checks failed.${NC}"
        exit $EXIT_CODE
    fi
fi
