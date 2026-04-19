import SearchIcon from "@mui/icons-material/Search";
import {
  Card,
  CardContent,
  InputAdornment,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";

import { StatusBadge } from "@/atoms/StatusBadge";
import { PageHeader } from "@/molecules/PageHeader";

import { type VerdictFilter, useConversationsPage } from "./ConversationsPage.hook";

export function ConversationsPage() {
  const { project, query, setQuery, verdict, setVerdict, filtered } = useConversationsPage();

  if (!project) {
    return <Typography>Project not found.</Typography>;
  }

  return (
    <>
      <PageHeader
        title="Conversations"
        subtitle="Every investigation in this project. Click one to replay."
      />

      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" spacing={2} mb={2}>
            <TextField
              size="small"
              placeholder="Search conversations"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
              }}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon fontSize="small" />
                    </InputAdornment>
                  ),
                },
              }}
              sx={{ flex: 1 }}
            />
            <TextField
              size="small"
              select
              label="Verdict"
              value={verdict}
              onChange={(e) => {
                setVerdict(e.target.value as VerdictFilter);
              }}
              sx={{ minWidth: 180 }}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="bug">Bug</MenuItem>
              <MenuItem value="business_condition">Business condition</MenuItem>
              <MenuItem value="unknown">Unknown</MenuItem>
            </TextField>
          </Stack>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Author</TableCell>
                <TableCell>Verdict</TableCell>
                <TableCell>Ticket</TableCell>
                <TableCell>Created</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.map((c) => (
                <TableRow key={c.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {c.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {c.preview}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{c.author}</Typography>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={c.verdict} />
                  </TableCell>
                  <TableCell>{c.hasTicket ? "Yes" : "—"}</TableCell>
                  <TableCell>
                    {formatDistanceToNowStrict(new Date(c.createdAtIso), { addSuffix: true })}
                  </TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5}>
                    <Typography variant="body2" color="text.secondary" align="center">
                      No conversations match your filters.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : null}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </>
  );
}
