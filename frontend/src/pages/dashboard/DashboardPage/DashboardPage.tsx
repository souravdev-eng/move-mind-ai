import AddIcon from "@mui/icons-material/Add";
import {
  Button,
  Card,
  CardContent,
  Link,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";
import { Link as RouterLink, useParams } from "react-router-dom";

import { KPIStat } from "@/atoms/KPIStat";
import { StatusBadge } from "@/atoms/StatusBadge";
import { conversations, projectsForOrg } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";

function formatEvents(n: number): string {
  if (n >= 1_000_000) {
    return `${(n / 1_000_000).toFixed(1)}M`;
  }
  if (n >= 1_000) {
    return `${(n / 1_000).toFixed(0)}K`;
  }
  return String(n);
}

export function DashboardPage() {
  const { orgSlug = "acme" } = useParams();
  const list = projectsForOrg(orgSlug);
  const totalEvents = list.reduce((sum, p) => sum + p.eventsLast24h, 0);
  const healthy = list.filter((p) => p.connectorStatus === "healthy").length;
  const drift = list.reduce((sum, p) => sum + p.driftAlerts, 0);
  const recent = conversations.slice(0, 3);

  return (
    <>
      <PageHeader
        title="Organisation dashboard"
        subtitle="Health, activity and spend across every project."
        actions={
          <Button
            variant="contained"
            size="small"
            startIcon={<AddIcon />}
            component={RouterLink}
            to={`/orgs/${orgSlug}/onboarding`}
          >
            New project
          </Button>
        }
      />

      <Stack direction="row" spacing={2} mb={3} flexWrap="wrap" useFlexGap>
        <KPIStat label="Projects" value={String(list.length)} />
        <KPIStat label="Healthy connectors" value={`${String(healthy)} / ${String(list.length)}`} />
        <KPIStat label="Events last 24h" value={formatEvents(totalEvents)} />
        <KPIStat
          label="Drift alerts"
          value={String(drift)}
          {...(drift === 0 ? { delta: "all clear", deltaPositive: true } : {})}
        />
      </Stack>

      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={600} mb={2}>
            Projects
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Project</TableCell>
                <TableCell>Connector</TableCell>
                <TableCell>Last sync</TableCell>
                <TableCell align="right">Events 24h</TableCell>
                <TableCell align="right">Eval score</TableCell>
                <TableCell>Drift</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {list.map((p) => (
                <TableRow key={p.id} hover>
                  <TableCell>
                    <Link component={RouterLink} to={`/orgs/${orgSlug}/projects/${p.slug}/overview`} underline="hover">
                      <Stack direction="row" spacing={1} alignItems="center">
                        <span aria-hidden="true">{p.icon}</span>
                        <Typography variant="body2" fontWeight={500}>
                          {p.name}
                        </Typography>
                      </Stack>
                    </Link>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={p.connectorStatus} />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {formatDistanceToNowStrict(new Date(p.lastSyncIso), { addSuffix: true })}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">{formatEvents(p.eventsLast24h)}</TableCell>
                  <TableCell align="right">{(p.evalScore * 100).toFixed(0)}%</TableCell>
                  <TableCell>
                    {p.driftAlerts > 0 ? <StatusBadge status="warning" /> : "—"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle1" fontWeight={600} mb={2}>
            Recent conversations
          </Typography>
          <Stack spacing={1.5}>
            {recent.map((c) => (
              <Stack
                key={c.id}
                direction="row"
                justifyContent="space-between"
                alignItems="center"
                spacing={2}
              >
                <Stack>
                  <Typography variant="body2" fontWeight={500}>
                    {c.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {c.author} •{" "}
                    {formatDistanceToNowStrict(new Date(c.createdAtIso), { addSuffix: true })}
                  </Typography>
                </Stack>
                <StatusBadge status={c.verdict} />
              </Stack>
            ))}
          </Stack>
        </CardContent>
      </Card>
    </>
  );
}
