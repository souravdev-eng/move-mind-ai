import { useContext } from "react";

import { ColorModeContext, type ColorModeContextValue } from "./ColorModeContext";

export function useColorMode(): ColorModeContextValue {
  const ctx = useContext(ColorModeContext);
  if (!ctx) {
    throw new Error("useColorMode must be used inside <ThemeProvider>");
  }
  return ctx;
}
