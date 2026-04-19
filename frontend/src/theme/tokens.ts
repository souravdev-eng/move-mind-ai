/**
 * Design tokens shared across light and dark themes.
 * Inspired by Supabase: neutral grays, single accent, tight scale, monospace for logs.
 * Do not read hardcoded values from these elsewhere — consume via `theme.*`.
 */

export const neutral = {
  50: "#fafafa",
  100: "#f4f4f5",
  200: "#e4e4e7",
  300: "#d4d4d8",
  400: "#a1a1aa",
  500: "#71717a",
  600: "#52525b",
  700: "#3f3f46",
  800: "#27272a",
  900: "#18181b",
  950: "#0a0a0a",
} as const;

export const accent = {
  50: "#ecfdf5",
  100: "#d1fae5",
  200: "#a7f3d0",
  300: "#6ee7b7",
  400: "#34d399",
  500: "#10b981",
  600: "#059669",
  700: "#047857",
  800: "#065f46",
  900: "#064e3b",
} as const;

export const semantic = {
  error: { main: "#ef4444", light: "#f87171", dark: "#b91c1c" },
  warning: { main: "#f59e0b", light: "#fbbf24", dark: "#b45309" },
  info: { main: "#3b82f6", light: "#60a5fa", dark: "#1d4ed8" },
  success: { main: "#10b981", light: "#34d399", dark: "#047857" },
} as const;

export const typography = {
  fontFamilyUi:
    "'Inter', 'IBM Plex Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  fontFamilyMono:
    "'JetBrains Mono', 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
  fontSizeBase: 14,
  fontWeightRegular: 400,
  fontWeightMedium: 500,
  fontWeightSemibold: 600,
  fontWeightBold: 700,
} as const;

export const shape = {
  borderRadius: 6,
  borderRadiusSmall: 4,
  borderRadiusLarge: 10,
} as const;

export const spacing = 8;

export type ColorMode = "light" | "dark";
