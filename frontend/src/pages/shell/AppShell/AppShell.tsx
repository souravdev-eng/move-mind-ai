import { Box, Toolbar } from "@mui/material";
import { Outlet } from "react-router-dom";

import { Breadcrumbs } from "@/pages/shell/Breadcrumbs";
import { DRAWER_WIDTH, LeftRail } from "@/pages/shell/LeftRail";
import { TopBar } from "@/pages/shell/TopBar";

export function AppShell() {
  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      <TopBar />
      <LeftRail />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { xs: `calc(100% - ${String(DRAWER_WIDTH)}px)` },
          px: 4,
          py: 3,
        }}
      >
        <Toolbar variant="dense" />
        <Breadcrumbs />
        <Outlet />
      </Box>
    </Box>
  );
}
