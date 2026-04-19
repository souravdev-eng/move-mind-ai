import { type ReactNode } from "react";

import { Box, Stack, Typography } from "@mui/material";

interface Props {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}

export function EmptyState({ title, description, icon, action }: Props) {
  return (
    <Stack
      alignItems="center"
      justifyContent="center"
      spacing={1.5}
      sx={{ py: 6, textAlign: "center" }}
    >
      {icon ? <Box sx={{ fontSize: 32 }}>{icon}</Box> : null}
      <Typography variant="subtitle1" fontWeight={600}>
        {title}
      </Typography>
      {description ? (
        <Typography variant="body2" color="text.secondary" maxWidth={360}>
          {description}
        </Typography>
      ) : null}
      {action}
    </Stack>
  );
}
