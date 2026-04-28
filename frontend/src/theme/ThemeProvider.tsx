import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";

import { CssBaseline, ThemeProvider as MuiThemeProvider } from "@mui/material";

import { ColorModeContext, type ColorModeContextValue } from "./ColorModeContext";
import { darkTheme } from "./darkTheme";
import { lightTheme } from "./lightTheme";
import { type ColorMode } from "./tokens";

const STORAGE_KEY = "move-mind.color-mode";

function readStoredMode(): ColorMode | null {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value === "light" || value === "dark" ? value : null;
  } catch {
    return null;
  }
}

function readSystemMode(): ColorMode {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return "dark";
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [mode, setModeState] = useState<ColorMode>(() => readStoredMode() ?? readSystemMode());

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = (event: MediaQueryListEvent) => {
      if (readStoredMode() === null) {
        setModeState(event.matches ? "dark" : "light");
      }
    };
    mq.addEventListener("change", handler);
    return () => {
      mq.removeEventListener("change", handler);
    };
  }, []);

  const setMode = useCallback((next: ColorMode) => {
    setModeState(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      /* storage unavailable — mode is still in memory for this session */
    }
  }, []);

  const toggleMode = useCallback(() => {
    setModeState((prev) => {
      const next: ColorMode = prev === "dark" ? "light" : "dark";
      try {
        localStorage.setItem(STORAGE_KEY, next);
      } catch {
        /* ignore */
      }
      return next;
    });
  }, []);

  const contextValue = useMemo<ColorModeContextValue>(
    () => ({ mode, setMode, toggleMode }),
    [mode, setMode, toggleMode]
  );

  const theme = mode === "dark" ? darkTheme : lightTheme;

  return (
    <ColorModeContext.Provider value={contextValue}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ColorModeContext.Provider>
  );
}
