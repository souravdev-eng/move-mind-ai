import { useEffect, useState } from "react";
import { ThemeProvider, CssBaseline, Container, Typography, Chip, Box } from "@mui/material";
import { theme } from "./theme";

type HealthStatus = "loading" | "ok" | "error";

function App() {
  const [health, setHealth] = useState<HealthStatus>("loading");

  useEffect(() => {
    fetch("/health")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => setHealth(data.status === "ok" ? "ok" : "error"))
      .catch(() => setHealth("error"));
  }, []);

  const chipColor = health === "ok" ? "success" : health === "error" ? "error" : "default";

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="sm" sx={{ mt: 8, textAlign: "center" }}>
        <Typography variant="h3" gutterBottom>
          Move Mind AI
        </Typography>
        <Box>
          <Chip label={`Backend: ${health}`} color={chipColor} variant="outlined" />
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
