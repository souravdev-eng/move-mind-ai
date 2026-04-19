---
trigger: model_decision
description: Full code review workflow — checks architecture placement, TypeScript strictness, styling tokens, state management, accessibility, and streaming/agentic UI patterns
---

# Code Review Workflow

Review the provided code against project standards. Check each category systematically.

## 1. Architecture Check

### File Location

- [ ] **Atoms** (`src/atoms/`): Basic UI elements (Button, Badge, StatusDot, StreamingCursor)
- [ ] **Molecules** (`src/molecules/`): Compositions of atoms (ChatInput, SourceCard, AgentNodeBadge)
- [ ] **Organisms** (`src/organisms/`): Complex features (ChatThread, AgentPipeline, SourcePanel, MessageBubble)
- [ ] **Pages** (`src/pages/`): Route-level views (ChatPage)
- [ ] **API client** (`src/api/`): `chatClient.ts` — REST + SSE, no business logic in route handlers
- [ ] **Context** (`src/context/`): `ChatContext.tsx` — global chat state only
- [ ] **Hooks** (`src/hooks/`): `useChat`, `useSSEStream`, `useAgentPipeline`, `usePreference`
- [ ] **Types** (`src/interfaces/`): All shared types — never re-declare locally

### File Structure

```
ComponentName/
├── ComponentName.tsx          # Main component (JSX + props interface)
├── ComponentName.style.tsx    # Styled components (theme-only!)
├── ComponentName.hook.tsx     # Business logic (if any)
└── index.ts                   # Re-export
```

### File Length Limits

| File Type    | Max Lines | Action if Exceeded             |
| ------------ | --------- | ------------------------------ |
| `.tsx`       | 400       | Split into `Layout/` subfolder |
| `.hook.tsx`  | 400       | Split into `hooks/` subfolder  |
| `.style.tsx` | 300       | Group related or split         |

## 2. TypeScript Check

- [ ] No unjustified `any` types
- [ ] Props interface defined at top of component file
- [ ] Return types specified for hooks
- [ ] Exported types for shared interfaces

```tsx
// ❌ Avoid
function process(data: any) { ... }

// ✅ Required
function process(data: UserData): ProcessedResult { ... }
```

## 3. Naming Conventions

| Type       | Convention                 | Example                              |
| ---------- | -------------------------- | ------------------------------------ |
| Components | PascalCase                 | `UserCard`, `NodeBadge`              |
| Hooks      | camelCase, prefix `use`    | `useJourneyData`, `useAuth`          |
| Utilities  | camelCase                  | `formatDate`, `parseJourney`         |
| Constants  | SCREAMING_SNAKE_CASE       | `MAX_RETRIES`, `NODE_TYPES`          |
| Interfaces | PascalCase                 | `UserData`, `ApiResponse`            |
| Files      | PascalCase matching export | `UserCard.tsx`, `UserCard.style.tsx` |

## 4. Component Pattern Check

```tsx
// Required pattern
export const ComponentName = memo(function ComponentName({ title, onAction }: ComponentNameProps) {
  const { data, isLoading, error, handleClick } = useComponentName({ onAction });

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage message="Something went wrong" />;
  if (!data) return <EmptyState />;

  return (
    <StyledContainer>
      <StyledTitle>{title}</StyledTitle>
      <Button onClick={handleClick}>Action</Button>
    </StyledContainer>
  );
});
```

- [ ] Uses `memo()` wrapper
- [ ] Named function (not arrow) inside memo
- [ ] Loading state handled
- [ ] Error state handled
- [ ] Empty state handled

## 5. Styling Check (CRITICAL)

**NEVER hardcode styling values. ALWAYS use theme.**

```tsx
// ❌ NEVER
backgroundColor: "#1976d2";
padding: "12px";
borderRadius: "4px";
fontSize: "14px";

// ✅ ALWAYS
backgroundColor: theme.palette.primary.main;
padding: theme.spacing(1.5);
borderRadius: theme.shape.borderRadius;
fontSize: theme.typography.body2.fontSize;
```

- [ ] No hardcoded colors (use `theme.palette`)
- [ ] No hardcoded spacing (use `theme.spacing()`)
- [ ] No hardcoded font sizes (use `theme.typography`)
- [ ] No hardcoded border radius (use `theme.shape.borderRadius`)
- [ ] Styles in separate `.style.tsx` file
- [ ] Custom props use `shouldForwardProp`

## 6. Accessibility Check

- [ ] Icon-only buttons have `aria-label`
- [ ] Semantic HTML used (`<nav>`, `<main>`, `<button>`)
- [ ] Keyboard support for interactive elements
- [ ] Tooltips on icon-only buttons

```tsx
// Required for icon buttons
<Tooltip title="Delete node">
  <IconButton aria-label="Delete node">
    <DeleteRoundedIcon />
  </IconButton>
</Tooltip>
```

## 7. State Management Check

| Data Type     | Use                     | Example                        |
| ------------- | ----------------------- | ------------------------------ |
| Chat messages | `ChatContext` + reducer | Message history, session_id    |
| Streaming     | Local state in hook     | Token buffer, node statuses    |
| Local UI      | `useState`              | Input value, panel open/closed |
| Preferences   | `localStorage` hook     | Dark mode, collapsed state     |

- [ ] No Redux, no TanStack Query, no Firebase
- [ ] Global chat state lives in `ChatContext` — not local to components
- [ ] Streaming token buffer is local to `useChat` / `useSSEStream`, not context
- [ ] No duplicate state (same data in multiple places)
- [ ] Derived values computed inline or with `useMemo`, not `useState` + `useEffect`
- [ ] Session ID persisted in context and re-sent with every turn

## Output Format

For each issue found:

1. **Category**: Architecture/TypeScript/Styling/etc.
2. **Issue**: What's wrong
3. **Location**: File and line number
4. **Fix**: How to correct it
5. **Code Example**: Show correct version

**Code to review:**

```
$ARGUMENTS
```
