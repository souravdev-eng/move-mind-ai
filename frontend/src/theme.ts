import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#90caf9" },
    secondary: { main: "#f48fb1" },
  },
  typography: {
    fontFamily: "'Inter', 'Roboto', sans-serif",
  },
});
