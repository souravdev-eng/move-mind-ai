import {
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";

import { StatusBadge } from "@/atoms/StatusBadge";
import { useActiveProject } from "@/hooks/useActiveProject";
import { ingestionRuns } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";
import { LogsTabs } from "@/pages/project/logs/LogsTabs";

function formatDuration(ms: number): string {
  if (ms === 0) {
    return "—";
  }
  const s = Math.round(ms / 1000);
  if (s < 60) {
    return `${String(s)}s`;
  }
  return `${String(Math.floor(s / 60))}m ${String(s % 60)}s`;
}

export function IngestionRunsPage() {
  const project = useActiveProject();
  if (!project) {
    return <Typography>Project not found.</Typography>;
  }
  const list = ingestionRuns.filter((r) => r.projectId === project.id);

  return (
    <>
      <PageHeader title="Logs" subtitle="Recent ingestion runs." />
      <LogsTabs />

      <Card variant="outlined">
        <CardContent>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Started</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell align="right">Events in</TableCell>
                <TableCell align="right">Events out</TableCell>
                <TableCell align="right">Cost</TableCell>
                <TableCell align="right">Errors</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {list.map((r) => (
                <TableRow key={r.id} hover>
                  <TableCell>
                    {formatDistanceToNowStrict(new Date(r.startedAtIso), { addSuffix: true })}
                  </TableCell>
                  <TableCell>{formatDuration(r.durationMs)}</TableCell>
                  <TableCell align="right">{r.eventsIn.toLocaleString("en-US")}</TableCell>
                  <TableCell align="right">{r.eventsOut.toLocaleString("en-US")}</TableCell>
                  <TableCell align="right">${r.embedCostUsd.toFixed(2)}</TableCell>
                  <TableCell align="right">{r.errorsCount}</TableCell>
                  <TableCell>
                    <StatusBadge status={r.status} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </>
  );
}
