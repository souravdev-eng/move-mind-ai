---
trigger: model_decision
description: Component and hook patterns for creating or editing React components — memo wrapper, state handling, hook structure, streaming variants, accessibility
---

# Component Pattern Rules

## Hook dependency policy (`react-hooks/exhaustive-deps`)

ESLint runs `exhaustive-deps` as a **warning**, not an error. Its suggestions are frequently wrong for memoized callbacks, refs, and objects created inside render — blindly adding the suggested dep can trigger infinite re-render loops or memory leaks.

**How to handle a warning:**

1. **Ask first: is the dep stable?** Function from `useCallback` with correct deps? Ref? Primitive prop? If yes — add it. The warning is correct.
2. **Is the dep an object/array literal created in render?** Don't add it directly; memoize it with `useMemo` / `useCallback`, then add the memoized value.
3. **Is the effect meant to run once on mount or on a subset of deps only?** Disable the rule *with a reason*:

   ```tsx
   // eslint-disable-next-line react-hooks/exhaustive-deps -- initial fetch only; `filters` changes handled by separate effect
   useEffect(() => { fetchOnce(); }, []);
   ```

   Rule: disable comment MUST include ` -- <reason>`. No reason → PR rejected. Generic reasons ("not needed", "safe") are not acceptable — name the specific invariant.

4. **Never silently delete the warning** by adding a fake dep (like a stable `true`) or by removing the effect. Fix the root cause or document the exception.

If you find yourself disabling `exhaustive-deps` more than once in the same file, the component has a state-shape problem — refactor into a reducer or extract the effect into a custom hook.

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
