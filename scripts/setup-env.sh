#!/bin/bash

# setup-env.sh — install or verify the Tailspin Toys development environment.
#
# Modes:
#   (default)              Install only what is missing or stale (idempotent).
#   --scope <scope>        Limit install to a subset of dependencies.
#                          Scope: server | client | app | e2e | all (default: all).
#                          `server` installs only Python deps; `app` adds Node
#                          modules; `e2e`/`all` also install the Playwright browser.
#   --force                Reinstall everything regardless of markers.
#   --check [scope]        Verify prerequisites without installing.
#                          Scope: server | client | app | e2e | all (default: all).
#                          `app` covers server + client (no Playwright browser).
#                          Exits non-zero with a remediation message when
#                          anything is missing.
#   --with-system-deps     Pass --with-deps to `playwright install`
#                          (opt-in; may require sudo on Linux).
#   --help                 Show this help.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLIENT_DIR="$PROJECT_ROOT/client"
SERVER_DIR="$PROJECT_ROOT/server"
VENV_DIR="$PROJECT_ROOT/venv"
REQUIREMENTS_FILE="$SERVER_DIR/requirements.txt"
PACKAGE_LOCK="$CLIENT_DIR/package-lock.json"
REQUIREMENTS_MARKER="$VENV_DIR/.requirements.sha256"
NODE_MODULES_MARKER="$CLIENT_DIR/node_modules/.package-lock.sha256"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

MODE="install"
FORCE=0
WITH_SYSTEM_DEPS=0
CHECK_SCOPE="all"
INSTALL_SCOPE="all"

usage() {
  sed -n '3,19p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      FORCE=1
      shift
      ;;
    --check)
      MODE="check"
      shift
      if [[ $# -gt 0 && "$1" != --* ]]; then
        CHECK_SCOPE="$1"
        shift
      fi
      ;;
    --scope)
      shift
      if [[ $# -gt 0 && "$1" != --* ]]; then
        INSTALL_SCOPE="$1"
        shift
      else
        echo -e "${RED}--scope requires a value (server|client|app|e2e|all)${NC}" >&2
        exit 2
      fi
      ;;
    --with-system-deps)
      WITH_SYSTEM_DEPS=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown argument: $1${NC}" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$CHECK_SCOPE" in
  server|client|app|e2e|all) ;;
  *)
    echo -e "${RED}Unknown --check scope: $CHECK_SCOPE (expected: server|client|app|e2e|all)${NC}" >&2
    exit 2
    ;;
esac

case "$INSTALL_SCOPE" in
  server|client|app|e2e|all) ;;
  *)
    echo -e "${RED}Unknown --scope: $INSTALL_SCOPE (expected: server|client|app|e2e|all)${NC}" >&2
    exit 2
    ;;
esac

sha256_of() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    sha256sum "$1" | awk '{print $1}'
  fi
}

python_version_tag() {
  python3 -c 'import sys; print(f"py{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")'
}

requirements_marker_value() {
  local req_hash
  req_hash=$(sha256_of "$REQUIREMENTS_FILE")
  local py_tag
  py_tag=$(python_version_tag)
  printf '%s %s\n' "$req_hash" "$py_tag"
}

# --- Check helpers ---------------------------------------------------------
# Each returns 0 when satisfied, non-zero (with a message on stderr) otherwise.

check_venv() {
  if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    echo -e "${RED}Missing Python virtual environment: $VENV_DIR${NC}" >&2
    return 1
  fi
  if [[ ! -f "$REQUIREMENTS_MARKER" ]]; then
    echo -e "${RED}Python dependencies not recorded as installed (missing $REQUIREMENTS_MARKER).${NC}" >&2
    return 1
  fi
  local expected actual
  expected=$(requirements_marker_value)
  actual=$(cat "$REQUIREMENTS_MARKER")
  if [[ "$expected" != "$actual" ]]; then
    echo -e "${RED}Python dependencies out of date (requirements.txt or Python version changed).${NC}" >&2
    return 1
  fi
  return 0
}

check_node_modules() {
  if [[ ! -d "$CLIENT_DIR/node_modules" ]]; then
    echo -e "${RED}Missing client/node_modules.${NC}" >&2
    return 1
  fi
  if [[ ! -f "$NODE_MODULES_MARKER" ]]; then
    echo -e "${RED}Client dependencies not recorded as installed (missing $NODE_MODULES_MARKER).${NC}" >&2
    return 1
  fi
  local expected actual
  expected=$(sha256_of "$PACKAGE_LOCK")
  actual=$(cat "$NODE_MODULES_MARKER")
  if [[ "$expected" != "$actual" ]]; then
    echo -e "${RED}Client dependencies out of date (package-lock.json changed).${NC}" >&2
    return 1
  fi
  return 0
}

check_playwright_browsers() {
  # `playwright install --dry-run chromium` exits 0 either way but reports
  # what would be installed. We treat any "downloading" / "install location"
  # mention combined with a missing executable as "needs install". The most
  # reliable signal is whether chromium.executablePath() resolves to an
  # existing file.
  if [[ ! -d "$CLIENT_DIR/node_modules/@playwright/test" ]]; then
    echo -e "${RED}@playwright/test is not installed in client/node_modules.${NC}" >&2
    return 1
  fi
  local exe
  exe=$(cd "$CLIENT_DIR" && node -e "import('@playwright/test').then(m => { try { console.log(m.chromium.executablePath()); } catch (e) { process.exit(1); } });" 2>/dev/null)
  if [[ -z "$exe" || ! -x "$exe" ]]; then
    echo -e "${RED}Playwright Chromium browser is not installed.${NC}" >&2
    return 1
  fi
  return 0
}

run_check() {
  local scope="$1"
  local failed=0
  case "$scope" in
    server)
      check_venv || failed=1
      ;;
    client)
      check_node_modules || failed=1
      ;;
    app)
      check_venv || failed=1
      check_node_modules || failed=1
      ;;
    e2e|all)
      check_venv || failed=1
      check_node_modules || failed=1
      check_playwright_browsers || failed=1
      ;;
  esac
  if [[ $failed -ne 0 ]]; then
    echo -e "${YELLOW}Run \`scripts/setup-env.sh\` to install missing prerequisites.${NC}" >&2
    return 1
  fi
  return 0
}

# --- Install helpers -------------------------------------------------------

install_python() {
  local need_install=0
  if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    need_install=1
  else
    # Recreate the venv if the Python interpreter version changed.
    local venv_py_tag system_py_tag
    venv_py_tag=$("$VENV_DIR/bin/python3" -c 'import sys; print(f"py{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || true)
    system_py_tag=$(python_version_tag)
    if [[ "$venv_py_tag" != "$system_py_tag" ]]; then
      echo -e "${YELLOW}Python version changed ($venv_py_tag -> $system_py_tag); recreating venv...${NC}"
      rm -r "$VENV_DIR"
      python3 -m venv "$VENV_DIR"
      need_install=1
    fi
  fi

  if [[ $FORCE -eq 1 ]]; then
    need_install=1
  elif [[ ! -f "$REQUIREMENTS_MARKER" ]]; then
    need_install=1
  else
    local expected actual
    expected=$(requirements_marker_value)
    actual=$(cat "$REQUIREMENTS_MARKER")
    [[ "$expected" != "$actual" ]] && need_install=1
  fi

  if [[ $need_install -eq 1 ]]; then
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    pip install -r "$REQUIREMENTS_FILE"
    requirements_marker_value > "$REQUIREMENTS_MARKER"
    deactivate
  else
    echo -e "${GREEN}Python dependencies already up to date.${NC}"
  fi
}

install_node_modules() {
  local need_install=0
  if [[ ! -d "$CLIENT_DIR/node_modules" ]]; then
    need_install=1
  elif [[ $FORCE -eq 1 ]]; then
    need_install=1
  elif [[ ! -f "$NODE_MODULES_MARKER" ]]; then
    need_install=1
  else
    local expected actual
    expected=$(sha256_of "$PACKAGE_LOCK")
    actual=$(cat "$NODE_MODULES_MARKER")
    [[ "$expected" != "$actual" ]] && need_install=1
  fi

  if [[ $need_install -eq 1 ]]; then
    echo -e "${BLUE}Installing client dependencies (npm ci)...${NC}"
    (cd "$CLIENT_DIR" && npm ci)
    sha256_of "$PACKAGE_LOCK" > "$NODE_MODULES_MARKER"
  else
    echo -e "${GREEN}Client dependencies already up to date.${NC}"
  fi
}

install_playwright_browsers() {
  if [[ $FORCE -ne 1 ]] && check_playwright_browsers 2>/dev/null; then
    echo -e "${GREEN}Playwright Chromium already installed.${NC}"
    return 0
  fi
  echo -e "${BLUE}Installing Playwright Chromium...${NC}"
  if [[ $WITH_SYSTEM_DEPS -eq 1 ]]; then
    (cd "$CLIENT_DIR" && npx playwright install --with-deps chromium)
  else
    (cd "$CLIENT_DIR" && npx playwright install chromium)
  fi
}

# --- Main ------------------------------------------------------------------

if [[ "$MODE" == "check" ]]; then
  run_check "$CHECK_SCOPE"
  exit $?
fi

echo -e "${BLUE}Setting up Tailspin Toys development environment...${NC}"
case "$INSTALL_SCOPE" in
  server)
    install_python
    ;;
  client)
    install_node_modules
    ;;
  app)
    install_python
    install_node_modules
    ;;
  e2e|all)
    install_python
    install_node_modules
    install_playwright_browsers
    ;;
esac
echo -e "${GREEN}Environment ready.${NC}"
