---
trigger: model_decision
description: UI/UX design standards for Move Mind AI — streaming message display, agent pipeline visualization, source citations, issue classification badges, MUI theme patterns
---

# UI/UX Design Standards

## Design Philosophy

**Intelligent, Transparent, Responsive.** Move Mind AI is a streaming AI debugging assistant — the UI must make the agent's reasoning process visible, legible, and trustworthy.

### Core Principles

| Principle          | Description                                                              |
| ------------------ | ------------------------------------------------------------------------ |
| **Transparency**   | Show the agent's work in real time — nodes, retrieval counts, sources.   |
| **Responsiveness** | Every token streams instantly. No full-page waits.                       |
| **Clarity**        | Complex AI output rendered in clean, scannable formats.                  |
| **Trust**          | Source citations and confidence indicators reduce hallucination anxiety. |

---

## Visual Language

### Color Usage

```tsx
// Primary actions, active states, links
theme.palette.primary.main;

// Secondary actions, subtle emphasis
theme.palette.secondary.main;

// Status colors - use semantically
theme.palette.success.main; // Success, active, enabled
theme.palette.error.main; // Errors, destructive actions, alerts
theme.palette.warning.main; // Warnings, caution states
theme.palette.info.main; // Information, tips

// Backgrounds
theme.palette.background.default; // Page background
theme.palette.background.paper; // Cards, panels, elevated surfaces

// Text hierarchy
theme.palette.text.primary; // Main content
theme.palette.text.secondary; // Supporting text, labels
theme.palette.text.disabled; // Disabled, placeholder
```

### Spacing System

Base unit: **8px**. Use consistent multipliers.

```tsx
theme.spacing(0.5); // 4px  - Tight: icon padding, badge padding
theme.spacing(1); // 8px  - Compact: between related items
theme.spacing(2); // 16px - Standard: component padding
theme.spacing(3); // 24px - Comfortable: section gaps
theme.spacing(4); // 32px - Spacious: major sections
```

### Typography Scale

```tsx
// Headings
theme.typography.h1; // Page titles (rarely used)
theme.typography.h2; // Section titles
theme.typography.h3; // Card titles
theme.typography.h4; // Subsection titles
theme.typography.h5; // Component titles
theme.typography.h6; // Small titles, labels

// Body
theme.typography.body1; // Primary content
theme.typography.body2; // Secondary content, descriptions
theme.typography.caption; // Timestamps, metadata, hints
```

### Border Radius

```tsx
theme.shape.borderRadius; // 8px - Standard (buttons, inputs, cards)
theme.shape.borderRadius * 0.5; // 4px - Tight (badges, chips)
theme.shape.borderRadius * 1.5; // 12px - Soft (modals, large cards)
theme.shape.borderRadius * 2; // 16px - Round (avatars, large buttons)
("50%"); // Circle (avatar images, indicators)
```

---

## Iconography

### Icon Style

Use **TwoTone** icons for navigation and primary UI elements. They provide a modern, premium feel.

```tsx
// ✅ Navigation icons - TwoTone
import SpaceDashboardTwoToneIcon from "@mui/icons-material/SpaceDashboardTwoTone";
import AccountTreeTwoToneIcon from "@mui/icons-material/AccountTreeTwoTone";
import SettingsTwoToneIcon from "@mui/icons-material/SettingsTwoTone";

// ✅ Action icons - Rounded
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import DeleteRoundedIcon from "@mui/icons-material/DeleteRounded";
import SaveRoundedIcon from "@mui/icons-material/SaveRounded";

// ❌ Avoid mixing styles
import DashboardIcon from "@mui/icons-material/Dashboard"; // Sharp
import DashboardOutlined from "@mui/icons-material/DashboardOutlined"; // Outlined
```

### Icon Contrast (Theme-Safe)

Icons must remain clearly visible in both light and dark modes.

```tsx
// ✅ Prefer semantic icon colors
color: theme.palette.text.secondary;

// ✅ Increase contrast for icons on tinted surfaces in dark mode
color: theme.palette.mode === "dark" ? theme.palette.text.primary : theme.palette.text.secondary;
```

**Native date/time input caveat:** browser picker icons often render black by default. For dark mode safety, hide native picker affordance and use themed `InputAdornment` icons.

### Icon Sizing

```tsx
// Navigation sidebar
fontSize: 22

// Toolbar buttons
fontSize: 20

// Inline with text
fontSize: 18 or 'small'

// Large feature icons
fontSize: 48
```

---

## Component Patterns

### Buttons

```tsx
// Primary action (one per view)
<Button variant="contained" color="primary">Save Journey</Button>

// Secondary action
<Button variant="outlined" color="primary">Cancel</Button>

// Destructive action
<Button variant="outlined" color="error">Delete</Button>

// Icon button with tooltip (always)
<Tooltip title="Delete node">
  <IconButton aria-label="Delete node">
    <DeleteRoundedIcon />
  </IconButton>
</Tooltip>
```

### Button Quality Standard

- Buttons should feel product-grade, not generic defaults.
- Keep one clear primary action per area.
- Use consistent radius, weight, and spacing (`theme.shape.borderRadius`, `theme.spacing`).
- Avoid overcrowding one row with many equal-priority buttons.
- Keep labels short and explicit (`Configure`, `Test Trigger`, `Save`).

```tsx
<Button
  size="small"
  variant="contained"
  startIcon={<TuneRoundedIcon />}
  sx={{
    borderRadius: (theme) => theme.spacing(1),
    textTransform: "none",
    fontWeight: 600,
  }}
>
  Configure
</Button>
```

### Cards & Panels

```tsx
// Elevated card
<Paper elevation={1} sx={{ p: 3, borderRadius: 1.5 }}>

// Flat card with border
<Box sx={{
  p: 2,
  border: 1,
  borderColor: 'divider',
  borderRadius: 1,
  bgcolor: 'background.paper'
}}>
```

### Form Fields

```tsx
// Standard input
<TextField
  size="small"
  fullWidth
  label="Journey Name"
  helperText="Enter a descriptive name"
/>

// Compact input (toolbars, inline edits)
<TextField
  size="small"
  variant="standard"
  sx={{ '& .MuiInputBase-input': { fontWeight: 600 } }}
/>
```

### Select & Modal Consistency

- Select controls and modal actions should follow shared spacing, border, radius, and typography tokens.
- Do not style select inputs in one-off ways that clash with rest of admin.
- For dense action sets, prefer a status `Select` over multiple small status buttons.

---

## AI Chat & Agentic UI Patterns

These patterns are mandatory for all chat and agent pipeline screens.

### 1) Streaming Message Display

- Render tokens as they arrive — **never buffer to completion**.
- Show a blinking cursor (`▊`) at the end of an in-progress stream.
- Use `white-space: pre-wrap` to preserve markdown line breaks during streaming.
- On `[DONE]`, replace raw streamed text with a proper markdown-rendered view.

```tsx
// StreamingMessage — append tokens live
const [buffer, setBuffer] = useState("");
const isStreaming = status === "streaming";

return (
  <Box sx={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>
    {buffer}
    {isStreaming && <StreamingCursor />}
  </Box>
);
```

### 2) Agent Pipeline Visualization

- Display each LangGraph node as a step with `pending → active → done` states.
- Node order: `classify_question → rewrite_question → resolve_context → retrieve_docs → rerank_docs → generate_answer → classify_issue`
- Show retrieval/rerank counts as inline badges when available.
- Collapse the pipeline after the answer is complete — keep it expandable.

```tsx
// AgentNodeBadge states
type NodeStatus = "pending" | "active" | "done" | "skipped";

// Active node: pulsing primary color
// Done node: success color + checkmark
// Pending node: muted text.disabled color
```

### 3) Source Citation Cards

- Always show sources below the final answer, never inline.
- Truncate `content` at 200 chars with a "Show more" expand.
- Surface key metadata as chips: `customer_id`, `journey_id`, `execution_id`, `status`, `error_code`.
- Group by `chunk_type` if multiple types appear.

### 4) Issue Classification Display

- Show `issue_type` as a prominent badge: `bug` → error color, `business_condition` → warning color, `unknown` → default.
- Display `issue_confidence` as a percentage next to the badge.
- Show `issue_classification_reason` in a collapsed accordion below.

### 5) Dynamic Theme Safety

- Verify all streaming components render correctly in both light and dark mode.
- Streaming cursor must be visible in both themes.
- Source card borders must use `theme.palette.divider`, not hardcoded colors.

---

## Animations & Transitions

### Timing Standards

```tsx
// Micro-interactions (hover, focus)
transition: "all 0.15s ease";

// UI state changes (expand, collapse)
transition: "all 0.2s ease";

// Page transitions, modals
transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)";

// Complex animations (theme toggle, drawer)
transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
```

### Hover Effects

```tsx
// Subtle lift
'&:hover': {
  transform: 'translateY(-2px)',
  boxShadow: theme.shadows[4],
}

// Scale pop
'&:hover': {
  transform: 'scale(1.02)',
}

// Background highlight
'&:hover': {
  backgroundColor: theme.palette.action.hover,
}

// Icon rotation (settings, refresh)
'&:hover .MuiSvgIcon-root': {
  transform: 'rotate(15deg)',
}
```

### Click Feedback

```tsx
'&:active': {
  transform: 'scale(0.98)',
}
```

### Loading States

```tsx
// Button loading
<Button disabled startIcon={<CircularProgress size={16} />}>
  Saving...
</Button>

// Content loading
<Skeleton variant="rectangular" height={200} />

// Full page loading
<Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
  <CircularProgress />
</Box>
```

---

## Dark Mode Support

### Design for Both Modes

```tsx
// ✅ Use semantic colors that adapt
backgroundColor: theme.palette.background.paper;
color: theme.palette.text.primary;
borderColor: theme.palette.divider;

// ❌ Never hardcode colors
backgroundColor: "#ffffff";
color: "#333333";
```

### Mode-Specific Adjustments

```tsx
// Conditional styling
backgroundColor: isDark
  ? 'rgba(255, 255, 255, 0.08)'  // Subtle light on dark
  : 'rgba(0, 0, 0, 0.04)',       // Subtle dark on light

// Shadow adjustments (darker shadows in light mode)
boxShadow: isDark
  ? '0 4px 12px rgba(0, 0, 0, 0.4)'
  : '0 4px 12px rgba(0, 0, 0, 0.1)',
```

### Theme Toggle

- Position: Header toolbar, easily accessible
- Animation: Smooth icon transition
- Persistence: Save preference to localStorage

---

## Responsive Design

### Breakpoints

```tsx
theme.breakpoints.up("xs"); // 0px+    Mobile
theme.breakpoints.up("sm"); // 600px+  Tablet
theme.breakpoints.up("md"); // 900px+  Desktop
theme.breakpoints.up("lg"); // 1200px+ Large desktop
theme.breakpoints.up("xl"); // 1536px+ Extra large
```

### Mobile Considerations

```tsx
// Collapsible sidebar on mobile
const isMobile = useMediaQuery(theme.breakpoints.down('md'));

// Touch-friendly targets (min 44px)
minHeight: 44,
minWidth: 44,

// Stack on mobile, row on desktop
flexDirection: { xs: 'column', md: 'row' }
```

---

## Navigation Patterns

### Sidebar

- **Collapsed**: Icon-only with tooltips
- **Expanded**: Icon + label + badges
- **Active state**: Background highlight + primary color
- **Hover**: Subtle background change

### Breadcrumbs

```tsx
<Breadcrumbs>
  <Link href="/">Journeys</Link>
  <Link href="/editor/abc">Journey Name</Link>
  <Typography color="text.primary">Edit Script</Typography>
</Breadcrumbs>
```

### Tabs

```tsx
<Tabs value={tab} onChange={handleChange}>
  <Tab label="Scripts" />
  <Tab label="Settings" />
  <Tab label="History" />
</Tabs>
```

---

## Feedback Patterns

### Success

```tsx
// Toast notification
<Snackbar>
  <Alert severity="success">Journey saved successfully</Alert>
</Snackbar>

// Inline
<Alert severity="success" sx={{ mt: 2 }}>Changes saved</Alert>
```

### Error

```tsx
// User-friendly message
<Alert severity="error">
  Unable to save. Please check your connection and try again.
</Alert>

// With action
<Alert
  severity="error"
  action={<Button size="small">Retry</Button>}
>
  Failed to load journeys
</Alert>
```

### Empty State

```tsx
<Box sx={{ textAlign: "center", py: 8 }}>
  <InboxIcon sx={{ fontSize: 64, color: "text.disabled" }} />
  <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
    No journeys yet
  </Typography>
  <Typography variant="body2" color="text.disabled">
    Create your first journey to get started
  </Typography>
  <Button variant="contained" sx={{ mt: 3 }}>
    Create Journey
  </Button>
</Box>
```

---

## Accessibility (Visual)

### Color Contrast

- Text on background: minimum 4.5:1 ratio
- Large text (18px+): minimum 3:1 ratio
- Interactive elements: clearly distinguishable

### Focus Indicators

```tsx
// Visible focus ring
'&:focus-visible': {
  outline: `2px solid ${theme.palette.primary.main}`,
  outlineOffset: 2,
}
```

### Motion Preferences

```tsx
// Respect reduced motion preference
'@media (prefers-reduced-motion: reduce)': {
  transition: 'none',
  animation: 'none',
}
```

---

## Checklist

### Before Shipping UI

**General**

- [ ] Uses theme values (no hardcoded colors/spacing)
- [ ] Icons are visible in both light and dark mode
- [ ] Has hover and active states
- [ ] Has error state with helpful message
- [ ] Has empty state designed
- [ ] Works in both light and dark mode
- [ ] Tooltips on icon-only buttons
- [ ] Keyboard accessible (Tab, Enter, Escape)
- [ ] Touch targets are 44px minimum
- [ ] Focus states are visible

**Streaming & Agentic UI (additional)**

- [ ] Tokens stream immediately — no buffering to completion
- [ ] Streaming cursor visible and animating during active stream
- [ ] Streaming text uses `white-space: pre-wrap`
- [ ] Post-stream: raw buffer replaced with markdown-rendered view
- [ ] Agent pipeline shows correct `pending / active / done` states per node
- [ ] Pipeline collapses gracefully after answer completes
- [ ] Source cards show all relevant metadata chips
- [ ] Issue type badge uses correct semantic color (`bug` → error, `business_condition` → warning)
- [ ] Issue confidence shown as percentage
- [ ] `[DONE]` event correctly finalizes the streaming state
- [ ] SSE error handled — user sees a retry option, not a blank screen
- [ ] Session ID persisted across turns for multi-turn context
