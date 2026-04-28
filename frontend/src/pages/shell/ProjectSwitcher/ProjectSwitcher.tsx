import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Box, Button, Menu, MenuItem, Typography } from "@mui/material";
import { useParams } from "react-router-dom";

import { useProjectSwitcher } from "./ProjectSwitcher.hook";

export function ProjectSwitcher() {
  const { projectSlug } = useParams();
  const { anchor, current, list, open, close, selectProject } = useProjectSwitcher();
  return (
    <>
      <Button
        size="small"
        color="inherit"
        endIcon={<ExpandMoreIcon />}
        onClick={open}
        aria-haspopup="menu"
      >
        {current ? (
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <span aria-hidden="true">{current.icon}</span>
            <span>{current.name}</span>
          </Box>
        ) : (
          "Select project"
        )}
      </Button>
      <Menu anchorEl={anchor} open={Boolean(anchor)} onClose={close}>
        {list.map((p) => (
          <MenuItem
            key={p.id}
            selected={p.slug === projectSlug}
            onClick={() => {
              selectProject(p.slug);
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <span aria-hidden="true">{p.icon}</span>
              <Box>
                <Typography variant="body2" fontWeight={500}>
                  {p.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {p.description}
                </Typography>
              </Box>
            </Box>
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}
