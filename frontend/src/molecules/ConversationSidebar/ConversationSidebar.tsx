import { useEffect, useState } from "react";

import AddIcon from "@mui/icons-material/Add";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import DeleteIcon from "@mui/icons-material/Delete";
import {
  Box,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";

import { listConversations } from "@/api/conversationClient";
import { type BackendConversation } from "@/interfaces/domain";

interface ConversationSidebarProps {
  currentSessionId: string | null;
  onSelectConversation: (sessionId: string) => void;
  onNewConversation: () => void;
  refreshTrigger?: number; // Increment to trigger refresh
}

export function ConversationSidebar({
  currentSessionId,
  onSelectConversation,
  onNewConversation,
  refreshTrigger,
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<BackendConversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");

  const loadConversations = async () => {
    try {
      const data = await listConversations();
      setConversations(data);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadConversations();
  }, [refreshTrigger]);

  const filtered = conversations.filter((c) =>
    filter === ""
      ? true
      : c.title?.toLowerCase().includes(filter.toLowerCase()) ??
      c.session_id.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <Paper
      elevation={0}
      sx={{
        height: "100%",
        borderRight: 1,
        borderColor: "divider",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
        <Stack direction="row" spacing={1} alignItems="center" mb={2}>
          <Typography variant="subtitle2" fontWeight={600} flex={1}>
            Conversations
          </Typography>
          <Tooltip title="New conversation">
            <IconButton size="small" onClick={onNewConversation}>
              <AddIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
        <TextField
          size="small"
          fullWidth
          placeholder="Search..."
          value={filter}
          onChange={(e) => {
            setFilter(e.target.value);
          }}
        />
      </Box>

      <List sx={{ flex: 1, overflowY: "auto", py: 0 }}>
        {loading ? (
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Loading...
            </Typography>
          </Box>
        ) : filtered.length === 0 ? (
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {filter ? "No matches" : "No conversations yet"}
            </Typography>
          </Box>
        ) : (
          filtered.map((c) => (
            <ListItem
              key={c.id}
              disablePadding
              secondaryAction={
                <IconButton edge="end" size="small" sx={{ opacity: 0.6 }}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              }
            >
              <ListItemButton
                selected={c.session_id === currentSessionId}
                onClick={() => {
                  onSelectConversation(c.session_id);
                }}
                dense
              >
                <ChatBubbleOutlineIcon
                  fontSize="small"
                  sx={{ mr: 1.5, color: "text.secondary" }}
                />
                <ListItemText
                  primary={
                    <Typography
                      variant="body2"
                      fontWeight={500}
                      noWrap
                      title={c.title ?? c.session_id}
                    >
                      {c.title ?? "New conversation"}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {formatDistanceToNowStrict(new Date(c.updated_at), {
                        addSuffix: true,
                      })}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))
        )}
      </List>
    </Paper>
  );
}
