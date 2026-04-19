import AddIcon from "@mui/icons-material/Add";
import {
  Button,
  Card,
  CardContent,
  Stack,
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
import { connectors } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";
import { LogsTabs } from "@/pages/project/logs/LogsTabs";

const kindLabel: Record<string, string> = {
  s3: "Amazon S3",
  cloudwatch: "CloudWatch",
  webhook: "Webhook",
  file_upload: "File upload",
  datadog: "Datadog",
  elastic: "Elastic",
  kafka: "Kafka",
};

export function ConnectorsPage() {
  const project = useActiveProject();
  if (!project) {
    return <Typography>Project not found.</Typography>;
  }
  const list = connectors.filter((c) => c.projectId === project.id);

  return (
    <>
      <PageHeader
        title="Logs"
        subtitle="Configured log sources for this project."
        actions={
          <Button size="small" variant="contained" startIcon={<AddIcon />} disabled>
            Add connector
          </Button>
        }
      />
      <LogsTabs />

      <Card variant="outlined">
        <CardContent>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Connector</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Schedule</TableCell>
                <TableCell>Last sync</TableCell>
                <TableCell align="right">Events 24h</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {list.map((c) => (
                <TableRow key={c.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {c.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {kindLabel[c.kind] ?? c.kind}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={c.status} />
                  </TableCell>
                  <TableCell>{c.scheduleLabel}</TableCell>
                  <TableCell>
                    {formatDistanceToNowStrict(new Date(c.lastSyncIso), { addSuffix: true })}
                  </TableCell>
                  <TableCell align="right">{c.eventsLast24h.toLocaleString("en-US")}</TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1} justifyContent="flex-end">
                      <Button size="small" disabled>
                        Sync now
                      </Button>
                      <Button size="small" disabled>
                        Edit
                      </Button>
                    </Stack>
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
