import { useEffect, useState } from "react";

import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";
import { Box, Chip, Container, IconButton, Tooltip, Typography } from "@mui/material";

import { ThemeProvider, useColorMode } from "./theme";

type HealthStatus = "loading" | "ok" | "error";

interface HealthResponse {
  status: string;
}

function ColorModeToggle() {
  const { mode, toggleMode } = useColorMode();
  const label = mode === "dark" ? "Switch to light mode" : "Switch to dark mode";
  return (
    <Tooltip title={label}>
      <IconButton aria-label={label} onClick={toggleMode} size="small">
        {mode === "dark" ? <LightModeIcon fontSize="small" /> : <DarkModeIcon fontSize="small" />}
      </IconButton>
    </Tooltip>
  );
}

function AppContent() {
  const [health, setHealth] = useState<HealthStatus>("loading");

  useEffect(() => {
    fetch("/health")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP ${String(res.status)}`);
        }
        return res.json() as Promise<HealthResponse>;
      })
      .then((data) => {
        setHealth(data.status === "ok" ? "ok" : "error");
      })
      .catch(() => {
        setHealth("error");
      });
  }, []);

  const chipColor = health === "ok" ? "success" : health === "error" ? "error" : "default";

  return (
    <Container maxWidth="sm" sx={{ mt: 8, textAlign: "center" }}>
      <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 2 }}>
        <ColorModeToggle />
      </Box>
      <Typography variant="h3" gutterBottom>
        Move Mind AI
      </Typography>
      <Box>
        <Chip label={`Backend: ${health}`} color={chipColor} variant="outlined" />
      </Box>
    </Container>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
