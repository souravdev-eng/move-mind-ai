import { createTheme, type Theme } from "@mui/material/styles";

import { accent, neutral, semantic, shape, spacing, typography } from "./tokens";

export const darkTheme: Theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: accent[500],
      light: accent[400],
      dark: accent[600],
      contrastText: neutral[950],
    },
    secondary: {
      main: neutral[200],
      contrastText: neutral[900],
    },
    background: {
      default: neutral[950],
      paper: neutral[900],
    },
    text: {
      primary: neutral[50],
      secondary: neutral[400],
      disabled: neutral[600],
    },
    divider: neutral[800],
    error: semantic.error,
    warning: semantic.warning,
    info: semantic.info,
    success: semantic.success,
    grey: neutral,
  },
  shape: { borderRadius: shape.borderRadius },
  spacing,
  typography: {
    fontFamily: typography.fontFamilyUi,
    fontSize: typography.fontSizeBase,
    fontWeightRegular: typography.fontWeightRegular,
    fontWeightMedium: typography.fontWeightMedium,
    fontWeightBold: typography.fontWeightBold,
    h1: { fontWeight: typography.fontWeightSemibold, letterSpacing: "-0.02em" },
    h2: { fontWeight: typography.fontWeightSemibold, letterSpacing: "-0.02em" },
    h3: { fontWeight: typography.fontWeightSemibold, letterSpacing: "-0.01em" },
    h4: { fontWeight: typography.fontWeightSemibold },
    h5: { fontWeight: typography.fontWeightSemibold },
    h6: { fontWeight: typography.fontWeightSemibold },
    button: { textTransform: "none", fontWeight: typography.fontWeightMedium },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          fontFeatureSettings: "'cv11', 'ss01', 'ss03'",
          WebkitFontSmoothing: "antialiased",
          MozOsxFontSmoothing: "grayscale",
        },
        "code, pre, kbd, samp": {
          fontFamily: typography.fontFamilyMono,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: shape.borderRadius,
          boxShadow: "none",
          "&:hover": { boxShadow: "none" },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: "none" },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: "none",
          borderBottom: `1px solid ${neutral[800]}`,
          backgroundColor: neutral[950],
        },
      },
    },
  },
});
