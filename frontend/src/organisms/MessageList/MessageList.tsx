import { Box, Stack, Typography } from "@mui/material";

import { StatusBadge } from "@/atoms/StatusBadge";
import { type PipelineNode } from "@/hooks/useChatStream";
import { type ChatMessage } from "@/interfaces/domain";
import { AgentPipeline } from "@/molecules/AgentPipeline";
import { ToolCallBlock } from "@/molecules/ToolCallBlock";

interface Props {
  messages: ChatMessage[];
  streaming: boolean;
  pipeline?: PipelineNode[];
}

export function MessageList({ messages, streaming: _streaming, pipeline = [] }: Props) {
  void _streaming; // kept in interface for API compat; pipeline replaces spinner

  // Find the index after the last user message — that's where the pipeline goes
  const pipelineInsertIdx = (() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages.at(i)?.role === "user") return i + 1;
    }
    return -1;
  })();

  return (
    <Stack spacing={2} sx={{ py: 2 }}>
      {messages.map((m, idx) => (
        <MessageBubbleWithPipeline
          key={m.id}
          message={m}
          showPipeline={idx === pipelineInsertIdx && pipeline.length > 0}
          pipeline={pipeline}
        />
      ))}
      {/* If pipeline exists but no assistant message yet, show it after all messages */}
      {pipelineInsertIdx === messages.length && pipeline.length > 0 ? (
        <AgentPipeline nodes={pipeline} />
      ) : null}
    </Stack>
  );
}

function MessageBubbleWithPipeline({
  message,
  showPipeline,
  pipeline,
}: {
  message: ChatMessage;
  showPipeline: boolean;
  pipeline: PipelineNode[];
}) {
  return (
    <>
      {showPipeline ? <AgentPipeline nodes={pipeline} /> : null}
      <MessageBubble message={message} />
    </>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  const isTool = message.role === "tool";

  if (isTool && message.toolCall) {
    return (
      <Box>
        <Typography variant="caption" color="text.secondary">
          {message.content}
        </Typography>
        <ToolCallBlock toolCall={message.toolCall} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        alignSelf: isUser ? "flex-end" : "flex-start",
        maxWidth: "80%",
        px: 2,
        py: 1.25,
        borderRadius: 1.5,
        bgcolor: isUser ? "primary.main" : "background.paper",
        color: isUser ? "primary.contrastText" : "text.primary",
        border: isUser ? 0 : 1,
        borderColor: "divider",
      }}
    >
      <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
        {message.content}
      </Typography>
      {message.verdict ? (
        <Box mt={1}>
          <StatusBadge status={message.verdict} />
        </Box>
      ) : null}
    </Box>
  );
}
