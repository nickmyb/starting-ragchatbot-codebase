# Frontend Code Quality Tools - Changes Made

## Overview

Added essential code quality tools to the frontend development workflow, including automatic code formatting with Prettier and JavaScript linting with ESLint.

## New Files Added

### 1. `package.json`
Node.js package configuration for frontend tooling.

**Contents:**
- Project metadata (name, version, description)
- npm scripts for quality checks:
  - `npm run format` - Auto-format all files with Prettier
  - `npm run format:check` - Check formatting without modifying files
  - `npm run lint` - Run ESLint to check for issues
  - `npm run lint:fix` - Auto-fix linting issues
  - `npm run quality` - Run all quality checks
  - `npm run quality:fix` - Auto-fix all issues
- Development dependencies: `eslint@^8.57.0`, `prettier@^3.2.5`
- Node.js engine requirement: `>=18.0.0`

### 2. `.prettierrc`
Prettier configuration for consistent code formatting.

**Settings:**
- `semi: true` - Always use semicolons
- `singleQuote: true` - Use single quotes in JavaScript
- `tabWidth: 4` - 4-space indentation
- `trailingComma: "es5"` - Trailing commas where valid in ES5
- `printWidth: 100` - Line width of 100 characters
- `endOfLine: "lf"` - Unix line endings
- HTML files: `printWidth: 120`
- CSS files: `singleQuote: false` (use double quotes)

### 3. `.prettierignore`
Files and directories to exclude from Prettier formatting.

**Excludes:**
- `node_modules/`
- `dist/`, `build/`
- Minified files (`*.min.js`, `*.min.css`)
- `package-lock.json`

### 4. `.eslintrc.json`
ESLint configuration for JavaScript code quality.

**Settings:**
- Environment: Browser + ES2021
- Extends: `eslint:recommended`
- Global: `marked` (readonly, for CDN library)
- Rules:
  - `no-unused-vars`: Warn (ignore args starting with `_`)
  - `no-console`: Off (allow console logging)
  - `semi`: Error (require semicolons)
  - `quotes`: Warn (prefer single quotes)
  - `indent`: Warn (4 spaces)
  - `no-var`: Warn (prefer `let`/`const`)
  - `prefer-const`: Warn (use `const` when possible)
  - `eqeqeq`: Warn (smart equality checking)

### 5. `quality.sh`
Bash script for running code quality checks.

**Usage:**
```bash
# Check formatting and linting (default)
./quality.sh

# Or explicitly
./quality.sh --check

# Auto-fix all issues
./quality.sh --fix

# Show help
./quality.sh -h
```

**Features:**
- Auto-installs dependencies if `node_modules/` missing
- Colored output for better readability
- Returns exit code 1 if checks fail (useful for CI)

## Modified Files

### 1. `.gitignore`
Added Node.js exclusions:
```
# Node.js (frontend tooling)
node_modules/
package-lock.json
```

### 2. `script.js`
Reformatted with Prettier for consistent code style:
- Consistent 4-space indentation
- Single quotes for strings
- Trailing commas in arrays/objects
- Proper spacing around operators
- Removed extra blank lines
- Changed `var` to `const` (lines 128-129)

### 3. `index.html`
Reformatted with Prettier:
- Lowercase `<!doctype html>`
- Self-closing tags with space before `/>`
- Consistent indentation (4 spaces)
- One attribute per line for elements with multiple attributes
- Changed escaped quotes in `data-question` to use single quotes around attribute

### 4. `style.css`
Minimal changes (already well-formatted):
- Ensured consistent formatting throughout

## How to Use

### Initial Setup
```bash
cd frontend
npm install
```

### Daily Development Workflow

**Check code quality before committing:**
```bash
./quality.sh
```

**Auto-fix issues:**
```bash
./quality.sh --fix
```

**Or use npm scripts directly:**
```bash
npm run quality      # Check all
npm run quality:fix  # Fix all
npm run format       # Format only
npm run lint         # Lint only
```

## Code Style Summary

| Aspect | Standard |
|--------|----------|
| Indentation | 4 spaces |
| Quotes (JS) | Single quotes |
| Quotes (CSS/HTML) | Double quotes |
| Semicolons | Always |
| Trailing commas | ES5-compatible |
| Line endings | LF (Unix) |
| Max line width | 100 chars (120 for HTML) |

## CI Integration

The quality checks return appropriate exit codes:
- Exit 0: All checks passed
- Exit 1: Issues found

Example GitHub Actions integration:
```yaml
- name: Frontend Quality Checks
  run: |
    cd frontend
    npm install
    npm run quality
```
