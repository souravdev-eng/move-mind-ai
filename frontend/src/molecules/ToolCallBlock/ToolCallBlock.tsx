import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Box, Collapse, IconButton, Stack, Typography } from "@mui/material";

import { type ToolCall } from "@/interfaces/domain";

import { useToolCallBlock } from "./ToolCallBlock.hook";

export function ToolCallBlock({ toolCall }: { toolCall: ToolCall }) {
  const { open, toggle } = useToolCallBlock();
  return (
    <Box
      sx={{
        border: 1,
        borderColor: "divider",
        borderRadius: 1,
        p: 1,
        my: 1,
        bgcolor: "action.hover",
      }}
    >
      <Stack direction="row" alignItems="center" spacing={1}>
        <IconButton
          size="small"
          onClick={toggle}
          aria-label={open ? "Collapse tool call" : "Expand tool call"}
          sx={{ transform: open ? "rotate(180deg)" : "rotate(0deg)", transition: "0.15s" }}
        >
          <ExpandMoreIcon fontSize="small" />
        </IconButton>
        <Typography variant="body2" fontFamily="monospace">
          {toolCall.name}
          {toolCall.server ? ` · ${toolCall.server}` : ""}
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Typography variant="caption" color="text.secondary">
          {toolCall.latencyMs} ms
        </Typography>
      </Stack>
      <Collapse in={open} unmountOnExit>
        <Stack spacing={1} sx={{ px: 2, py: 1 }}>
          <Labelled label="input" text={toolCall.input} />
          <Labelled label="output" text={toolCall.output} />
        </Stack>
      </Collapse>
    </Box>
  );
}

function Labelled({ label, text }: { label: string; text: string }) {
  return (
    <Box>
      <Typography variant="overline" color="text.secondary">
        {label}
      </Typography>
      <Box
        component="pre"
        sx={{
          fontFamily: "monospace",
          fontSize: 12,
          whiteSpace: "pre-wrap",
          m: 0,
          mt: 0.25,
        }}
      >
        {text}
      </Box>
    </Box>
  );
}
