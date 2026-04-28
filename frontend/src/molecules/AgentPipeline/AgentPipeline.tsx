import { useState } from "react";

import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { type PipelineNode } from "@/hooks/useChatStream";

const NODE_LABELS: Record<string, string> = {
  classify_question: "Classifying",
  rewrite_question: "Rewriting",
  resolve_context: "Resolving context",
  retrieve_docs: "Retrieving",
  rerank_docs: "Reranking",
  generate_answer: "Generating",
  classify_issue: "Classifying issue",
};

interface Props {
  nodes: PipelineNode[];
}

export function AgentPipeline({ nodes }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (nodes.length === 0) return null;

  const allDone = nodes.every((n) => n.status === "done");
  const runningNode = nodes.find((n) => n.status === "running");
  const doneCount = nodes.filter((n) => n.status === "done").length;

  if (allDone && !expanded) {
    return (
      <Stack
        direction="row"
        alignItems="center"
        spacing={0.5}
        sx={{
          py: 0.5,
          px: 1,
          borderRadius: 1,
          bgcolor: "action.hover",
          width: "fit-content",
          cursor: "pointer",
        }}
        onClick={() => {
          setExpanded(true);
        }}
      >
        <CheckCircleOutlineIcon sx={{ fontSize: 14 }} color="success" />
        <Typography variant="caption" color="text.secondary">
          {String(nodes.length)} steps completed
        </Typography>
        <ExpandMoreIcon sx={{ fontSize: 14 }} color="action" />
      </Stack>
    );
  }

  return (
    <Box
      sx={{
        py: 0.75,
        px: 1.5,
        borderRadius: 1,
        bgcolor: "action.hover",
        width: "fit-content",
        maxWidth: "100%",
      }}
    >
      {allDone ? (
        <Stack
          direction="row"
          alignItems="center"
          spacing={0.5}
          sx={{ cursor: "pointer", mb: 0.5 }}
          onClick={() => {
            setExpanded(false);
          }}
        >
          <CheckCircleOutlineIcon sx={{ fontSize: 14 }} color="success" />
          <Typography variant="caption" color="text.secondary">
            {String(nodes.length)} steps completed
          </Typography>
          <IconButton size="small" sx={{ p: 0 }}>
            <ExpandMoreIcon sx={{ fontSize: 14, transform: "rotate(180deg)" }} />
          </IconButton>
        </Stack>
      ) : (
        <Stack direction="row" alignItems="center" spacing={0.5} mb={0.5}>
          <CircularProgress size={12} />
          <Typography variant="caption" color="text.primary" fontWeight={500}>
            {runningNode ? (NODE_LABELS[runningNode.name] ?? runningNode.name) : "Processing"}…
          </Typography>
          <Typography variant="caption" color="text.disabled">
            ({String(doneCount)}/{String(nodes.length)})
          </Typography>
        </Stack>
      )}
      <Collapse in={!allDone || expanded}>
        <Stack spacing={0.25} sx={{ pl: 0.5 }}>
          {nodes.map((node) => (
            <Stack key={node.name} direction="row" alignItems="center" spacing={0.5}>
              {node.status === "running" ? (
                <CircularProgress size={10} />
              ) : (
                <CheckCircleOutlineIcon sx={{ fontSize: 12 }} color="success" />
              )}
              <Typography
                variant="caption"
                sx={{ fontSize: 11 }}
                color={node.status === "running" ? "text.primary" : "text.disabled"}
              >
                {NODE_LABELS[node.name] ?? node.name}
              </Typography>
            </Stack>
          ))}
        </Stack>
      </Collapse>
    </Box>
  );
}
