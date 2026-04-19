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

import { StatusBadge } from "@/atoms/StatusBadge";
import { useActiveProject } from "@/hooks/useActiveProject";
import { mcpServers } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";
import { SectionTabs } from "@/molecules/SectionTabs";

export function McpServersPage() {
  const project = useActiveProject();
  const { orgSlug = "acme", projectSlug = "" } = useParams();
  if (!project) {
    return <Typography>Project not found.</Typography>;
  }
  const list = mcpServers.filter((s) => s.projectId === project.id);
  const base = `/orgs/${orgSlug}/projects/${projectSlug}/code-context`;

  return (
    <>
      <PageHeader
        title="Code Context"
        subtitle="Connect code servers so the agent can ground answers in source."
        actions={
          <Button size="small" variant="contained" startIcon={<AddIcon />} disabled>
            Add MCP server
          </Button>
        }
      />
      <SectionTabs
        tabs={[
          { label: "MCP Servers", to: `${base}/mcp` },
          { label: "Hosted Repo Index", to: `${base}/repo-index` },
        ]}
      />

      <Card variant="outlined">
        <CardContent>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Server</TableCell>
                <TableCell>Transport</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last heartbeat</TableCell>
                <TableCell align="right">Tools</TableCell>
                <TableCell align="right">Resources</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {list.map((s) => (
                <TableRow key={s.id} hover>
                  <TableCell>
                    <Link
                      component={RouterLink}
                      to={`${base}/mcp/${s.id}`}
                      underline="hover"
                    >
                      <Stack>
                        <Typography variant="body2" fontWeight={500}>
                          {s.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" fontFamily="monospace">
                          {s.endpoint}
                        </Typography>
                      </Stack>
                    </Link>
                  </TableCell>
                  <TableCell>{s.transport.toUpperCase()}</TableCell>
                  <TableCell>
                    <StatusBadge status={s.status} />
                  </TableCell>
                  <TableCell>
                    {formatDistanceToNowStrict(new Date(s.lastHeartbeatIso), { addSuffix: true })}
                  </TableCell>
                  <TableCell align="right">{s.tools.length}</TableCell>
                  <TableCell align="right">{s.resources.length}</TableCell>
                </TableRow>
              ))}
              {list.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6}>
                    <Typography align="center" variant="body2" color="text.secondary">
                      No MCP servers connected for this project.
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
