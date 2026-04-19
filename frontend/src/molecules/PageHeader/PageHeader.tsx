import { type ReactNode } from "react";

import { Box, Stack, Typography } from "@mui/material";

interface Props {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, subtitle, actions }: Props) {
  return (
    <Stack direction="row" alignItems="flex-start" justifyContent="space-between" mb={3}>
      <Box>
        <Typography variant="h5" fontWeight={600}>
          {title}
        </Typography>
        {subtitle ? (
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            {subtitle}
          </Typography>
        ) : null}
      </Box>
      {actions ? <Stack direction="row" spacing={1}>{actions}</Stack> : null}
    </Stack>
  );
}
