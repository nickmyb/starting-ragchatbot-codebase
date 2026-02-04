# Frontend Changes: Theme Toggle Button & Light Theme CSS Variables

## Summary
Added a complete dark/light theme system with:
- Theme toggle button for switching between themes
- CSS custom properties (CSS variables) for all theme-aware colors
- `data-theme` attribute on the `<html>` element for theme switching
- All existing elements work well in both themes
- Maintained visual hierarchy and design language

## Files Modified

### `frontend/index.html`
- Added theme toggle button in the sidebar (top-right position)
- Uses SVG icons for sun (light mode indicator) and moon (dark mode indicator)
- Includes accessibility attributes (`aria-label`, `title`)
- Updated cache-busting version numbers for CSS and JS files

### `frontend/style.css`

#### New CSS Variables Added
Extended the CSS variable system with additional theme-aware variables:

**Dark Theme (`:root`):**
- `--chip-bg`: `rgba(255, 255, 255, 0.06)` - Source chip background
- `--chip-border`: `rgba(255, 255, 255, 0.1)` - Source chip border
- `--chip-hover-bg`: `rgba(255, 255, 255, 0.12)` - Source chip hover background
- `--chip-hover-border`: `rgba(255, 255, 255, 0.25)` - Source chip hover border
- `--error-bg`: `rgba(239, 68, 68, 0.1)` - Error message background
- `--error-color`: `#f87171` - Error text color
- `--error-border`: `rgba(239, 68, 68, 0.2)` - Error message border
- `--success-bg`: `rgba(34, 197, 94, 0.1)` - Success message background
- `--success-color`: `#4ade80` - Success text color
- `--success-border`: `rgba(34, 197, 94, 0.2)` - Success message border
- `--welcome-shadow`: `rgba(0, 0, 0, 0.2)` - Welcome message shadow

**Light Theme (`[data-theme="light"]`):**
- All base variables adjusted for light backgrounds
- `--chip-bg`: `rgba(0, 0, 0, 0.04)` - Subtle chip background
- `--chip-border`: `rgba(0, 0, 0, 0.1)` - Visible chip border
- `--chip-hover-bg`: `rgba(0, 0, 0, 0.08)` - Darker hover state
- `--chip-hover-border`: `rgba(0, 0, 0, 0.2)` - Stronger hover border
- `--error-color`: `#dc2626` - Darker red for contrast (WCAG AA)
- `--success-color`: `#16a34a` - Darker green for contrast (WCAG AA)
- `--code-bg`: `rgba(15, 23, 42, 0.06)` - Subtle code block background
- `--focus-ring`: `rgba(37, 99, 235, 0.3)` - Stronger focus visibility
- `--welcome-shadow`: `rgba(0, 0, 0, 0.08)` - Lighter shadow

#### Updated Styles
- `.source-chip` - Now uses CSS variables for background/border
- `.error-message` - Now uses CSS variables for colors
- `.success-message` - Now uses CSS variables for colors
- `.welcome-message` - Now uses CSS variable for shadow

#### Theme Toggle Styles
- Circular button (40px) positioned absolutely in top-right of sidebar
- Smooth hover/focus/active state transitions
- Icon switching logic using CSS (moon in dark mode, sun in light mode)
- Rotation animation class for toggle effect
- Responsive styles for mobile (36px on smaller screens)

#### Smooth Theme Transitions
Added a global transition rule for smooth theme switching. The following elements have 0.3s ease transitions on `background-color`, `color`, `border-color`, and `box-shadow`:

- `body`, `.container`, `.main-content` - Page-level backgrounds
- `.sidebar` - Sidebar background and borders
- `.chat-main`, `.chat-container`, `.chat-messages` - Chat area backgrounds
- `.chat-input-container` - Input area background and border
- `.message-content` - Message bubble backgrounds
- `.message-content code`, `.message-content pre` - Code blocks
- `.message-content blockquote` - Blockquote styling
- `.stat-item` - Course stats card backgrounds
- `.suggested-item` - Suggested question buttons
- `.source-chip` - Source citation chips
- `.sources-collapsible` - Sources dropdown
- `.error-message`, `.success-message` - Alert messages
- `.theme-toggle` - Toggle button itself
- `#chatInput`, `#sendButton` - Input field and send button
- `.new-chat-button` - New chat button text
- `.stats-header`, `.suggested-header` - Collapsible section headers
- `.course-title-item` - Individual course titles
- `.loading span` - Loading animation dots

#### Bug Fix
- Fixed `.message-content blockquote` using undefined `var(--primary)` → `var(--primary-color)`

### `frontend/script.js`
- Added `themeToggle` DOM element reference
- Added `initializeTheme()` function:
  - Loads saved theme from localStorage
  - Falls back to system preference (`prefers-color-scheme`)
  - Listens for system theme changes
- Added `setTheme()` function to apply theme
- Added `toggleTheme()` function with rotation animation
- Added `updateThemeToggleLabel()` for dynamic accessibility labels
- Added keyboard event handlers (Enter/Space) for accessibility

## Features

1. **Icon-based design**: Uses sun and moon SVG icons that match the existing icon style
2. **Position**: Top-right corner of the sidebar
3. **Smooth animations**:
   - 0.3s ease transition on all theme-aware colors (background, text, borders, shadows)
   - Scale transform on hover (1.05) and active (0.95) for toggle button
   - 360-degree rotation animation when toggling
   - All UI elements transition smoothly between themes without jarring changes
4. **Accessibility**:
   - Full keyboard navigation support (Tab, Enter, Space)
   - Dynamic `aria-label` that updates based on current theme
   - `title` attribute for tooltip
   - Focus ring matching existing focus styles
   - WCAG AA compliant color contrast ratios
5. **Persistence**: Theme preference saved to localStorage
6. **System preference**: Respects `prefers-color-scheme` when no saved preference exists

## JavaScript Functionality

The theme toggle is powered by the following JavaScript functions:

### `initializeTheme()`
- Called on page load (`DOMContentLoaded`)
- Checks localStorage for saved theme preference
- Falls back to system preference via `prefers-color-scheme` media query
- Defaults to dark theme if no preference found
- Sets up listener for system theme changes

### `setTheme(theme)`
- Applies theme by setting/removing `data-theme="light"` attribute on `<html>`
- Updates toggle button's accessibility labels

### `toggleTheme()`
- Triggered by click or keyboard (Enter/Space) on toggle button
- Determines current theme and switches to opposite
- Adds rotation animation class (removed after 300ms)
- Saves new preference to localStorage

### `updateThemeToggleLabel(theme)`
- Updates `aria-label` and `title` attributes dynamically
- Shows "Switch to dark theme" in light mode
- Shows "Switch to light theme" in dark mode

## Theme Color Reference

### Dark Theme (default)
| Variable | Value | Description |
|----------|-------|-------------|
| `--background` | `#0f172a` | Main background |
| `--surface` | `#1e293b` | Card/sidebar background |
| `--surface-hover` | `#334155` | Hover state background |
| `--text-primary` | `#f1f5f9` | Primary text (contrast: 15.4:1) |
| `--text-secondary` | `#94a3b8` | Secondary text (contrast: 7.2:1) |
| `--border-color` | `#334155` | Border color |
| `--primary-color` | `#2563eb` | Primary accent |

### Light Theme
| Variable | Value | Description |
|----------|-------|-------------|
| `--background` | `#f8fafc` | Main background |
| `--surface` | `#ffffff` | Card/sidebar background |
| `--surface-hover` | `#f1f5f9` | Hover state background |
| `--text-primary` | `#1e293b` | Primary text (contrast: 12.6:1) |
| `--text-secondary` | `#64748b` | Secondary text (contrast: 4.7:1) |
| `--border-color` | `#e2e8f0` | Border color |
| `--primary-color` | `#2563eb` | Primary accent |

## Accessibility Standards

- **Text contrast**: All text colors meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
- **Error/Success colors**: Adjusted for light theme to maintain readability
- **Focus indicators**: Visible focus rings on all interactive elements
- **Keyboard navigation**: Full keyboard support for theme toggle

## Implementation Details

### CSS Custom Properties Architecture
The theme system uses CSS custom properties (CSS variables) defined at two levels:

1. **`:root`** - Dark theme (default)
   - All color variables defined here serve as the default/fallback
   - Variables cascade down to all elements

2. **`[data-theme="light"]`** - Light theme override
   - Applied to `<html>` element via JavaScript
   - Overrides only the color values, not the structure
   - CSS specificity ensures light values take precedence

### Theme Attribute
The `data-theme` attribute is applied to `document.documentElement` (the `<html>` element):
- **Dark mode**: No attribute (uses `:root` defaults)
- **Light mode**: `data-theme="light"` attribute present

This approach:
- Allows CSS selectors like `[data-theme="light"] .element` for theme-specific styles
- Works with CSS custom property inheritance
- Is performant (single attribute change triggers all transitions)

### Elements Using CSS Variables
All existing elements use CSS variables for their colors:

| Element | Properties Using Variables |
|---------|---------------------------|
| Body/Container | `background-color`, `color` |
| Sidebar | `background`, `border-color` |
| Chat messages | `background`, `color`, `border-color` |
| User messages | `background` (uses `--user-message`) |
| Assistant messages | `background` (uses `--surface`), `color` |
| Input field | `background`, `border-color`, `color` |
| Buttons | `background`, `color`, hover states |
| Source chips | `background`, `border-color`, `color` |
| Code blocks | `background-color` (uses `--code-bg`) |
| Scrollbars | `background` for track and thumb |
| Focus rings | `box-shadow` (uses `--focus-ring`) |

### Visual Hierarchy Preservation
Both themes maintain the same visual hierarchy:
- Primary actions (send button) use `--primary-color`
- Surface elevation: `--background` < `--surface` < `--surface-hover`
- Text hierarchy: `--text-primary` for main content, `--text-secondary` for labels
- Borders use `--border-color` consistently for separation
