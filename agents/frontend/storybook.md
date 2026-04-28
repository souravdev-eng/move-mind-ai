---
trigger: model_decision
description: Storybook guidelines (planned, not yet installed) — story templates for AgentNodeBadge, StreamingCursor, SourceCard, IssueClassBadge atoms and molecules
---

# Storybook Guidelines

> **Status: Planned — not yet installed.**
> Storybook is not in `package.json` yet. When it is set up, follow these guidelines.
> Until then, use visual review in the dev browser for UI validation.

## Requirements (when installed)

| Level         | Storybook Required |
| ------------- | ------------------ |
| **Atoms**     | Yes                |
| **Molecules** | Yes                |
| **Organisms** | No                 |
| **Pages**     | No                 |

## Priority Atoms & Molecules to Story

| Component         | Why it needs stories                        |
| ----------------- | ------------------------------------------- |
| `StreamingCursor` | Must validate blink animation, theme safety |
| `StatusDot`       | Must show pending / active / done states    |
| `AgentNodeBadge`  | All three node statuses + badge variants    |
| `SourceCard`      | Truncation, expand, all metadata chips      |
| `IssueClassBadge` | bug / business_condition / unknown variants |
| `ChatInput`       | Empty, typed, loading, disabled states      |

## Template

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { AgentNodeBadge } from "./AgentNodeBadge";

const meta: Meta<typeof AgentNodeBadge> = {
  title: "Molecules/AgentNodeBadge",
  component: AgentNodeBadge,
  tags: ["autodocs"],
  parameters: { layout: "centered" },
  argTypes: {
    status: { control: "select", options: ["pending", "active", "done"] },
  },
};

export default meta;
type Story = StoryObj<typeof AgentNodeBadge>;

export const Pending: Story = { args: { label: "Classify", status: "pending" } };
export const Active: Story = { args: { label: "Classify", status: "active" } };
export const Done: Story = { args: { label: "Classify", status: "done" } };
export const WithBadge: Story = { args: { label: "Retrieve", status: "done", badge: "12" } };
```

## Naming Convention

```
title: 'Atoms/ComponentName'      // For atoms
title: 'Molecules/ComponentName'  // For molecules
```

## Checklist (when writing stories)

- [ ] Story file co-located with component
- [ ] Default story exists
- [ ] All status/variant states covered
- [ ] Streaming/animated components have a `Static` story for snapshot testing
- [ ] Both light and dark theme verified in Storybook
- [ ] `argTypes` configured for key props
- [ ] `layout: 'centered'` for standalone atoms/molecules
