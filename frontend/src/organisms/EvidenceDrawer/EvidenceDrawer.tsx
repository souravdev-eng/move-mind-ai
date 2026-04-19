import { Box, Stack, Typography } from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";

import { type EvidenceItem } from "@/interfaces/domain";

export function EvidenceDrawer({ items }: { items: EvidenceItem[] }) {
  return (
    <Box
      sx={{
        borderLeft: 1,
        borderColor: "divider",
        bgcolor: "background.paper",
        p: 2,
        overflowY: "auto",
      }}
    >
      <Typography variant="subtitle2" fontWeight={600} mb={1.5}>
        Evidence
      </Typography>
      {items.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          Evidence will appear here as the agent retrieves logs and code.
        </Typography>
      ) : (
        <Stack spacing={1.5}>
          {items.map((ev) => (
            <Box
              key={ev.id}
              sx={{
                border: 1,
                borderColor: "divider",
                borderRadius: 1,
                p: 1,
              }}
            >
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="caption" color="text.secondary">
                  {ev.source}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatDistanceToNowStrict(new Date(ev.timestampIso), { addSuffix: true })}
                </Typography>
              </Stack>
              <Box
                component="pre"
                sx={{
                  mt: 0.75,
                  fontFamily: "monospace",
                  fontSize: 12,
                  whiteSpace: "pre-wrap",
                  m: 0,
                }}
              >
                {ev.snippet}
              </Box>
              <Typography variant="caption" color="text.disabled">
                id: {ev.correlationId}
              </Typography>
            </Box>
          ))}
        </Stack>
      )}
    </Box>
  );
}
