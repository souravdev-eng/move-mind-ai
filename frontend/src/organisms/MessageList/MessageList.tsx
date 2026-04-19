import { Box, CircularProgress, Stack, Typography } from "@mui/material";

import { StatusBadge } from "@/atoms/StatusBadge";
import { type ChatMessage } from "@/interfaces/domain";
import { ToolCallBlock } from "@/molecules/ToolCallBlock";

interface Props {
  messages: ChatMessage[];
  streaming: boolean;
}

export function MessageList({ messages, streaming }: Props) {
  return (
    <Stack spacing={2} sx={{ py: 2 }}>
      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}
      {streaming ? (
        <Stack direction="row" alignItems="center" spacing={1} color="text.secondary">
          <CircularProgress size={14} />
          <Typography variant="caption">Agent is thinking…</Typography>
        </Stack>
      ) : null}
    </Stack>
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
