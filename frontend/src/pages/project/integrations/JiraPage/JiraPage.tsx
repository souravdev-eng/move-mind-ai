import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  IconButton,
  Link,
  MenuItem,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";

import { StatusBadge } from "@/atoms/StatusBadge";
import type { jiraConfigs, jiraTickets } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";

import { type TabKey, useJiraPage } from "./JiraPage.hook";

export function JiraPage() {
  const { project, tab, setTab, config, tickets } = useJiraPage();

  if (!project) {
    return <Typography>Project not found.</Typography>;
  }

  return (
    <>
      <PageHeader
        title="Jira"
        subtitle="Create tickets from investigations. Manager-triggered only (SOW §10)."
        actions={
          config?.connected ? (
            <StatusBadge status="connected" />
          ) : (
            <Button size="small" variant="contained">
              Connect Atlassian
            </Button>
          )
        }
      />

      <Tabs
        value={tab}
        onChange={(_e, v: TabKey) => {
          setTab(v);
        }}
        sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}
      >
        <Tab value="connect" label="Connect" />
        <Tab value="mapping" label="Mapping" />
        <Tab value="activity" label="Activity" />
      </Tabs>

      {tab === "connect" ? <ConnectTab config={config} /> : null}
      {tab === "mapping" ? <MappingTab /> : null}
      {tab === "activity" ? <ActivityTab tickets={tickets} /> : null}
    </>
  );
}

function ConnectTab({ config }: { config: ReturnType<typeof jiraConfigs.find> }) {
  return (
    <Card variant="outlined">
      <CardContent>
        {config?.connected ? (
          <Stack spacing={2}>
            <Row label="Site" value={config.site} />
            <Row label="Jira project" value={config.jiraProjectKey} />
            <Row label="Default issue type" value={config.defaultIssueType} />
            <Row label="Default priority" value={config.defaultPriority} />
            <Stack direction="row" spacing={1}>
              <Button size="small" variant="outlined">
                Create test ticket
              </Button>
              <Button size="small" color="error" variant="text">
                Disconnect
              </Button>
            </Stack>
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            This project is not connected to Jira. Connect above to map verdicts to tickets.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

function MappingTab() {
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={3}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Verdict → Jira labels
            </Typography>
            <Stack direction="row" spacing={1} mt={1} flexWrap="wrap" useFlexGap>
              <Chip label="bug → movemind/bug" />
              <Chip label="business_condition → movemind/biz-rule" />
              <Chip label="unknown → movemind/needs-triage" />
            </Stack>
          </Box>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Field mapping
            </Typography>
            <Stack spacing={1.5} mt={1}>
              <TextField
                size="small"
                label="Summary"
                value="{{ title }}"
                slotProps={{ input: { readOnly: true } }}
              />
              <TextField
                size="small"
                label="Description"
                multiline
                minRows={3}
                value="{{ technical_report }}\n\n## Steps to reproduce\n{{ steps_to_reproduce }}"
                slotProps={{ input: { readOnly: true } }}
              />
              <TextField size="small" select label="Assignee strategy" defaultValue="round-robin">
                <MenuItem value="round-robin">Round-robin from team</MenuItem>
                <MenuItem value="last-editor">Last code editor</MenuItem>
                <MenuItem value="fixed">Fixed assignee</MenuItem>
              </TextField>
            </Stack>
          </Box>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Triggering rules
            </Typography>
            <Typography variant="body2" color="text.secondary" mt={0.5}>
              Tickets are only created when a manager explicitly triggers the flow from an
              investigation.
            </Typography>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}

function ActivityTab({ tickets }: { tickets: typeof jiraTickets }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Key</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Verdict</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Assignee</TableCell>
              <TableCell>Created</TableCell>
              <TableCell />
            </TableRow>
          </TableHead>
          <TableBody>
            {tickets.map((t) => (
              <TableRow key={t.id} hover>
                <TableCell>
                  <Typography variant="body2" fontFamily="monospace">
                    {t.key}
                  </Typography>
                </TableCell>
                <TableCell>{t.title}</TableCell>
                <TableCell>
                  <StatusBadge status={t.verdict} />
                </TableCell>
                <TableCell>
                  <StatusBadge status={t.status} />
                </TableCell>
                <TableCell>{t.assignee}</TableCell>
                <TableCell>
                  {formatDistanceToNowStrict(new Date(t.createdAtIso), { addSuffix: true })}
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    component={Link}
                    href={t.url}
                    target="_blank"
                    rel="noopener"
                    aria-label={`Open ${t.key} in Jira`}
                  >
                    <OpenInNewIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {tickets.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7}>
                  <Typography align="center" variant="body2" color="text.secondary">
                    No tickets have been created yet.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <Stack direction="row" justifyContent="space-between">
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2">{value}</Typography>
    </Stack>
  );
}
