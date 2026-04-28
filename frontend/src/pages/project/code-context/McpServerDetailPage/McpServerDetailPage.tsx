import { type ReactNode } from "react";

import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import WarningIcon from "@mui/icons-material/Warning";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Stack,
  Switch,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tabs,
  Typography,
} from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";
import { Link as RouterLink } from "react-router-dom";

import { StatusBadge } from "@/atoms/StatusBadge";
import { PageHeader } from "@/molecules/PageHeader";

import { type TabKey, useMcpServerDetailPage } from "./McpServerDetailPage.hook";

export function McpServerDetailPage() {
  const { tab, setTab, server, nav, backTo } = useMcpServerDetailPage();

  if (!server) {
    return (
      <Stack spacing={2}>
        <Typography>Server not found.</Typography>
        <Button
          onClick={() => {
            nav(-1);
          }}
        >
          Back
        </Button>
      </Stack>
    );
  }

  return (
    <>
      <PageHeader
        title={server.name}
        subtitle={`${server.transport.toUpperCase()} · ${server.endpoint}`}
        actions={
          <>
            <Button
              size="small"
              startIcon={<ArrowBackIcon />}
              component={RouterLink}
              to={backTo}
              variant="text"
            >
              Back
            </Button>
            <StatusBadge status={server.status} />
          </>
        }
      />

      <Tabs
        value={tab}
        onChange={(_e, v: TabKey) => {
          setTab(v);
        }}
        sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}
      >
        <Tab value="tools" label={`Tools (${String(server.tools.length)})`} />
        <Tab value="resources" label={`Resources (${String(server.resources.length)})`} />
        <Tab value="invocations" label={`Invocations (${String(server.invocations.length)})`} />
        <Tab value="health" label="Health" />
      </Tabs>

      {tab === "tools" ? (
        <Card variant="outlined">
          <CardContent>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Input schema</TableCell>
                  <TableCell align="right">Calls 24h</TableCell>
                  <TableCell>Write</TableCell>
                  <TableCell>Whitelisted</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {server.tools.map((t) => (
                  <TableRow key={t.name}>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {t.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{t.description}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" fontFamily="monospace" color="text.secondary">
                        {t.inputSchema}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{t.callsLast24h}</TableCell>
                    <TableCell>
                      {t.writeCapable ? (
                        <Chip
                          size="small"
                          color="warning"
                          icon={<WarningIcon fontSize="small" />}
                          label="Write"
                        />
                      ) : (
                        <Chip size="small" variant="outlined" label="Read" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Switch size="small" checked={t.whitelisted} readOnly />
                    </TableCell>
                  </TableRow>
                ))}
                {server.tools.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6}>
                      <Typography align="center" color="text.secondary" variant="body2">
                        Waiting on handshake to enumerate tools.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : null}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : null}

      {tab === "resources" ? (
        <Card variant="outlined">
          <CardContent>
            <Stack spacing={2}>
              {server.resources.map((r) => (
                <Stack key={r.uriTemplate} spacing={0.5}>
                  <Typography variant="body2" fontFamily="monospace">
                    {r.uriTemplate}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {r.description}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Last read:{" "}
                    {r.lastReadIso
                      ? formatDistanceToNowStrict(new Date(r.lastReadIso), { addSuffix: true })
                      : "never"}
                  </Typography>
                </Stack>
              ))}
              {server.resources.length === 0 ? (
                <Typography color="text.secondary" variant="body2">
                  No resources exposed.
                </Typography>
              ) : null}
            </Stack>
          </CardContent>
        </Card>
      ) : null}

      {tab === "invocations" ? (
        <Card variant="outlined">
          <CardContent>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>When</TableCell>
                  <TableCell>Tool</TableCell>
                  <TableCell>Input</TableCell>
                  <TableCell>Output</TableCell>
                  <TableCell align="right">Latency</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {server.invocations.map((inv) => (
                  <TableRow key={inv.id}>
                    <TableCell>
                      {formatDistanceToNowStrict(new Date(inv.atIso), { addSuffix: true })}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {inv.toolName}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" fontFamily="monospace" color="text.secondary">
                        {inv.inputPreview}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" fontFamily="monospace" color="text.secondary">
                        {inv.outputPreview}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{inv.latencyMs} ms</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : null}

      {tab === "health" ? (
        <Card variant="outlined">
          <CardContent>
            <Stack spacing={1.5}>
              <Row label="Status" value={<StatusBadge status={server.status} />} />
              <Row
                label="Last heartbeat"
                value={formatDistanceToNowStrict(new Date(server.lastHeartbeatIso), {
                  addSuffix: true,
                })}
              />
              <Row label="Tools enumerated" value={String(server.tools.length)} />
            </Stack>
            <Box mt={3}>
              <Typography variant="overline" color="text.secondary">
                Danger zone
              </Typography>
              <Stack direction="row" spacing={1} mt={1}>
                <Button size="small" variant="outlined">
                  Rotate token
                </Button>
                <Button size="small" color="error">
                  Revoke connection
                </Button>
              </Stack>
            </Box>
          </CardContent>
        </Card>
      ) : null}
    </>
  );
}

function Row({ label, value }: { label: string; value: ReactNode }) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="center">
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Box>{value}</Box>
    </Stack>
  );
}
