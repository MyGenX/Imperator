#!/usr/bin/env bash
set -e

REPO="${IMPERATOR_REPO:-https://github.com/MyGenX/Imperator}"
IMPERATOR_DIR="${IMPERATOR_DIR:-$HOME/.imperator}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

echo ""
echo -e "${BOLD}👑 Imperator Installer${NC}"
echo -e "────────────────────────────────"
echo ""

check_dep() {
  if ! command -v "$1" &>/dev/null; then
    echo -e "${RED}✗ $1 is required but not installed.${NC}"
    echo -e "  Install it and re-run this script."
    exit 1
  fi
}

echo -e "${BLUE}→ Checking dependencies...${NC}"
check_dep git
check_dep python3
check_dep pip3
echo -e "${GREEN}✓ All dependencies found${NC}"
echo ""

if [ -d "$IMPERATOR_DIR/.git" ]; then
  echo -e "${YELLOW}→ Imperator already installed. Updating...${NC}"
  git -C "$IMPERATOR_DIR" pull --quiet
  echo -e "${GREEN}✓ Updated to latest version${NC}"
else
  echo -e "${BLUE}→ Cloning Imperator...${NC}"
  git clone --quiet "$REPO" "$IMPERATOR_DIR"
  echo -e "${GREEN}✓ Cloned to $IMPERATOR_DIR${NC}"
fi
echo ""

echo -e "${BLUE}→ Installing Python CLI...${NC}"
pip3 install -e "$IMPERATOR_DIR/cli" --quiet
echo -e "${GREEN}✓ CLI installed (entry point: imperator)${NC}"
echo ""

echo -e "${BOLD}${GREEN}✓ Imperator installed successfully!${NC}"
echo ""
echo -e "  Run ${BOLD}imperator init${NC} in your project to get started"
echo -e "  Docs: ${BLUE}${REPO}${NC}"
echo ""
