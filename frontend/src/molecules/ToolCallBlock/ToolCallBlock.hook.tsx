import { useState } from "react";

export function useToolCallBlock() {
  const [open, setOpen] = useState(false);
  const toggle = () => {
    setOpen((v) => !v);
  };
  return { open, toggle };
}
