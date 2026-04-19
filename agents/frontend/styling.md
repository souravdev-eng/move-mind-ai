---
trigger: glob
description: MUI theme styling rules — loaded when editing style or component files. Includes streaming animation patterns for Move Mind AI.
globs: "frontend/src/**/*.style.tsx,frontend/src/**/*.tsx"
---

# Styling Rules

**NEVER hardcode styling values. ALWAYS use MUI theme.**

## Required Theme Tokens

| Category  | ❌ Never                  | ✅ Always                                |
| --------- | ------------------------- | ---------------------------------------- |
| Colors    | `'#1976d2'`, `'rgb(...)'` | `theme.palette.primary.main`             |
| Spacing   | `'12px'`, `'16px'`        | `theme.spacing(1.5)`, `theme.spacing(2)` |
| Font size | `'14px'`                  | `theme.typography.body2.fontSize`        |
| Radius    | `'4px'`                   | `theme.shape.borderRadius`               |

## Style File Pattern

```tsx
// ComponentName.style.tsx
import { styled } from "@mui/material/styles";

export const StyledContainer = styled(Box, {
  shouldForwardProp: (prop) => prop !== "isActive",
})<{ isActive?: boolean }>(({ theme, isActive }) => ({
  padding: theme.spacing(2),
  backgroundColor: isActive ? theme.palette.primary.light : theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
}));
```

## Streaming & Animation Patterns

Define animations directly in `styled()` — never in inline `sx` keyframes unless unavoidable.

```tsx
// ✅ Streaming cursor blink
export const StyledStreamingCursor = styled(Box)(({ theme }) => ({
  display: "inline-block",
  width: 2,
  height: "1em",
  backgroundColor: theme.palette.primary.main,
  marginLeft: theme.spacing(0.25),
  verticalAlign: "middle",
  animation: "blink 1s step-end infinite",
  "@keyframes blink": {
    "0%, 100%": { opacity: 1 },
    "50%": { opacity: 0 },
  },
}));

// ✅ Active agent node pulse
export const StyledActiveNode = styled(Chip)(({ theme }) => ({
  color: theme.palette.primary.main,
  backgroundColor: theme.palette.primary.light,
  animation: "pulse 1.2s ease-in-out infinite",
  "@keyframes pulse": {
    "0%, 100%": { opacity: 1 },
    "50%": { opacity: 0.5 },
  },
}));
```

## Rules

- Styles in separate `.style.tsx` files, never inline
- Use `styled()` from `@mui/material/styles`
- Custom props must use `shouldForwardProp`
- Verify icon/text visibility in both light and dark mode
- Streaming cursors and node pulse animations must work in both themes
- Respect `prefers-reduced-motion`: wrap animations in `@media (prefers-reduced-motion: no-preference)`
