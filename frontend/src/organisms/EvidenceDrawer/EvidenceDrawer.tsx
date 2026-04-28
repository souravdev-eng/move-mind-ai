import { useState } from "react";

import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Badge, Box, Chip, Collapse, IconButton, Stack, Typography } from "@mui/material";

import { type SourceDocumentDTO } from "@/interfaces/domain";

interface Props {
  sources: SourceDocumentDTO[];
}

export function EvidenceDrawer({ sources }: Props) {
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
      <Stack direction="row" alignItems="center" spacing={1} mb={1.5}>
        <Typography variant="subtitle2" fontWeight={600}>
          Evidence
        </Typography>
        {sources.length > 0 ? (
          <Badge
            badgeContent={sources.length}
            color="primary"
            sx={{ "& .MuiBadge-badge": { fontSize: 10, height: 16, minWidth: 16 } }}
          />
        ) : null}
      </Stack>
      {sources.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          Evidence will appear here as the agent retrieves logs and code.
        </Typography>
      ) : (
        <Stack spacing={1}>
          {sources.map((src, idx) => (
            <EvidenceCard
              key={`${src.execution_id}-${src.chunk_type}-${String(idx)}`}
              source={src}
            />
          ))}
        </Stack>
      )}
    </Box>
  );
}

function buildSummary(src: SourceDocumentDTO): string {
  const parts: string[] = [];
  if (src.action) parts.push(src.action);
  if (src.page_path) parts.push(src.page_path);
  if (src.step_order != null) parts.push(`step ${String(src.step_order)}`);
  if (parts.length > 0) return parts.join(" · ");
  return src.content.slice(0, 80) + (src.content.length > 80 ? "…" : "");
}

function EvidenceCard({ source: src }: { source: SourceDocumentDTO }) {
  const [open, setOpen] = useState(false);

  return (
    <Box
      sx={{
        border: 1,
        borderColor: "divider",
        borderRadius: 1,
        overflow: "hidden",
      }}
    >
      {/* Summary header — always visible */}
      <Stack
        direction="row"
        alignItems="center"
        spacing={0.5}
        sx={{
          px: 1,
          py: 0.5,
          cursor: "pointer",
          "&:hover": { bgcolor: "action.hover" },
        }}
        onClick={() => {
          setOpen((p) => !p);
        }}
      >
        <IconButton size="small" sx={{ p: 0 }}>
          <ExpandMoreIcon
            sx={{
              fontSize: 16,
              transform: open ? "rotate(180deg)" : "rotate(0deg)",
              transition: "transform 0.2s",
            }}
          />
        </IconButton>
        <Stack direction="row" spacing={0.5} flexWrap="wrap" alignItems="center" flex={1}>
          {src.chunk_type ? (
            <Chip
              label={src.chunk_type}
              size="small"
              variant="outlined"
              sx={{ height: 18, fontSize: 10 }}
            />
          ) : null}
          {src.status ? (
            <Chip
              label={src.status}
              size="small"
              color={src.status === "failed" ? "error" : "default"}
              variant="outlined"
              sx={{ height: 18, fontSize: 10 }}
            />
          ) : null}
          <Typography variant="caption" color="text.secondary" noWrap sx={{ fontSize: 11 }}>
            {buildSummary(src)}
          </Typography>
        </Stack>
      </Stack>

      {/* Collapsible detail */}
      <Collapse in={open}>
        <Box sx={{ px: 1, pb: 1 }}>
          <Box
            component="pre"
            sx={{
              fontFamily: "monospace",
              fontSize: 11,
              lineHeight: 1.4,
              whiteSpace: "pre-wrap",
              m: 0,
              p: 0.75,
              borderRadius: 0.5,
              bgcolor: "action.hover",
              maxHeight: 200,
              overflowY: "auto",
            }}
          >
            {src.content}
          </Box>
          <Stack direction="row" spacing={1} mt={0.5} flexWrap="wrap">
            {src.customer_id ? (
              <Typography variant="caption" color="text.disabled" sx={{ fontSize: 10 }}>
                CID: {src.customer_id}
              </Typography>
            ) : null}
            {src.journey_id ? (
              <Typography variant="caption" color="text.disabled" sx={{ fontSize: 10 }}>
                journey: {src.journey_id}
              </Typography>
            ) : null}
            {src.execution_id ? (
              <Typography variant="caption" color="text.disabled" sx={{ fontSize: 10 }}>
                exec: {src.execution_id}
              </Typography>
            ) : null}
          </Stack>
        </Box>
      </Collapse>
    </Box>
  );
}
