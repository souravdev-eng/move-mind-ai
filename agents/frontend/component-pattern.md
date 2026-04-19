---
trigger: model_decision
description: Component and hook patterns for creating or editing React components — memo wrapper, state handling, hook structure, streaming variants, accessibility
---

# Component Pattern Rules

## Standard Component Structure

```tsx
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

## Streaming Component Structure

For components that receive live token/event updates, keep streaming state **local** to minimize re-renders.

```tsx
// ✅ Token-driven component — state local, memo isolates re-renders
export const StreamingText = memo(function StreamingText({
  content,
  isStreaming,
}: StreamingTextProps) {
  if (!isStreaming) {
    return <MarkdownView content={content} />;
  }

  return (
    <Box sx={{ whiteSpace: "pre-wrap" }}>
      {content}
      <StreamingCursor />
    </Box>
  );
});
```

## Required Elements

1. **Use `memo()` wrapper** with named function inside (not arrow function)
2. **Handle all states**:
   - Loading → `<Skeleton />`
   - Streaming → `<StreamingText isStreaming />` with cursor
   - Error → `<ErrorMessage message="..." />`
   - Empty → `<EmptyState />`
3. **Never expose raw errors** to users

## Hook Pattern

```tsx
interface UseComponentNameProps {
  onAction: () => void;
}

interface UseComponentNameReturn {
  data: Data | undefined;
  isLoading: boolean;
  isStreaming: boolean;
  error: Error | null;
  handleClick: () => void;
}

export function useComponentName({ onAction }: UseComponentNameProps): UseComponentNameReturn {
  // Business logic here
}
```

## Performance Rules for Streaming Components

- **`memo()` is mandatory** on any component that receives `content` or `isStreaming` props.
- Never pass streaming state down more than 2 levels — lift the streaming hook, not the state.
- Use `useCallback` on any handler passed to a memoized child.

## Accessibility

- Icon-only buttons need `aria-label`
- Use semantic HTML (`<nav>`, `<main>`, `<button>`)
- Add keyboard support for interactive elements
- Wrap icon buttons with `<Tooltip>`
- Live streaming text regions: use `aria-live="polite"` on the streaming container
