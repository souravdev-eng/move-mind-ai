import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Button, Menu, MenuItem } from "@mui/material";

import { useOrgSwitcher } from "./OrgSwitcher.hook";

export function OrgSwitcher() {
  const { anchor, current, orgs, open, close, selectOrg } = useOrgSwitcher();
  if (!current) {
    return null;
  }
  return (
    <>
      <Button
        size="small"
        color="inherit"
        endIcon={<ExpandMoreIcon />}
        onClick={open}
        aria-haspopup="menu"
      >
        {current.name}
      </Button>
      <Menu anchorEl={anchor} open={Boolean(anchor)} onClose={close}>
        {orgs.map((o) => (
          <MenuItem
            key={o.id}
            selected={o.slug === current.slug}
            onClick={() => {
              selectOrg(o.slug);
            }}
          >
            {o.name}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}
