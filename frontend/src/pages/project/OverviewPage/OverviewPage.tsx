import { type ReactNode } from "react";

import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";
import { Link as RouterLink, useParams } from "react-router-dom";

import { KPIStat } from "@/atoms/KPIStat";
import { StatusBadge } from "@/atoms/StatusBadge";
import { useActiveProject } from "@/hooks/useActiveProject";
import { cms3Descriptor, conversations } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";

export function OverviewPage() {
  const { orgSlug = "acme" } = useParams();
  const project = useActiveProject();
  if (!project) {
    return <Typography>Project not found.</Typography>;
  }
  const projectConvs = conversations.filter((c) => c.projectId === project.id).slice(0, 4);

  return (
    <>
      <PageHeader
        title={project.name}
        subtitle={project.description}
        actions={
          <>
            <Button
              variant="outlined"
              size="small"
              component={RouterLink}
              to={`/orgs/${orgSlug}/projects/${project.slug}/logs/schema`}
            >
              View descriptor
            </Button>
            <Button
              variant="contained"
              size="small"
              component={RouterLink}
              to={`/orgs/${orgSlug}/projects/${project.slug}/investigate`}
            >
              Ask a question
            </Button>
          </>
        }
      />

      <Stack direction="row" spacing={2} mb={3} flexWrap="wrap" useFlexGap>
        <KPIStat label="Connector" value={project.connectorStatus} />
        <KPIStat
          label="Last sync"
          value={formatDistanceToNowStrict(new Date(project.lastSyncIso), { addSuffix: true })}
        />
        <KPIStat label="Events 24h" value={project.eventsLast24h.toLocaleString("en-US")} />
        <KPIStat
          label="Eval score"
          value={`${String(Math.round(project.evalScore * 100))}%`}
          delta={`${project.evalTrend >= 0 ? "+" : ""}${(project.evalTrend * 100).toFixed(1)} pts`}
          deltaPositive={project.evalTrend >= 0}
        />
      </Stack>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} mb={1.5}>
                Descriptor
              </Typography>
              <Stack direction="row" spacing={1} mb={2} flexWrap="wrap" useFlexGap>
                <Chip
                  label={`domain: ${cms3Descriptor.domainId}`}
                  size="small"
                  variant="outlined"
                />
                <Chip
                  label={`version: ${project.descriptorVersion}`}
                  size="small"
                  variant="outlined"
                />
                <Chip
                  label={`primary key: ${cms3Descriptor.correlationKeys.primary.value}`}
                  size="small"
                  variant="outlined"
                />
              </Stack>
              <Typography variant="body2" color="text.secondary" mb={2}>
                {cms3Descriptor.domainDescription}
              </Typography>
              <Box>
                <Typography variant="overline" color="text.secondary">
                  Vocabulary
                </Typography>
                <Stack direction="row" spacing={1} mt={0.5} flexWrap="wrap" useFlexGap>
                  <Chip size="small" label={`event: ${cms3Descriptor.vocabulary.eventUnit}`} />
                  <Chip size="small" label={`flow: ${cms3Descriptor.vocabulary.flowUnit}`} />
                  <Chip size="small" label={`actor: ${cms3Descriptor.vocabulary.actorUnit}`} />
                  <Chip size="small" label={`routing: ${cms3Descriptor.vocabulary.routingUnit}`} />
                </Stack>
              </Box>
            </CardContent>
          </Card>

          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} mb={1.5}>
                Recent conversations
              </Typography>
              {projectConvs.length === 0 ? (
                <Typography color="text.secondary" variant="body2">
                  No conversations yet.
                </Typography>
              ) : (
                <Stack spacing={1.5}>
                  {projectConvs.map((c) => (
                    <Stack
                      key={c.id}
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
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
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 5 }}>
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} mb={1.5}>
                Health
              </Typography>
              <Stack spacing={1.5}>
                <HealthRow
                  label="Connector"
                  value={<StatusBadge status={project.connectorStatus} />}
                />
                <HealthRow
                  label="Drift alerts"
                  value={project.driftAlerts > 0 ? <StatusBadge status="warning" /> : "None"}
                />
                <HealthRow
                  label="Pinecone namespace"
                  value={
                    <Typography variant="body2" fontFamily="monospace">
                      {project.pineconeNamespace}
                    </Typography>
                  }
                />
              </Stack>
            </CardContent>
          </Card>

          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} mb={1.5}>
                Next steps
              </Typography>
              <Stack spacing={1}>
                <Typography variant="body2">• Connect a code server for code grounding</Typography>
                <Typography variant="body2">
                  • Connect Jira to create tickets from investigations
                </Typography>
                <Typography variant="body2">• Invite your team from Settings</Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </>
  );
}

function HealthRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="center">
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      {value}
    </Stack>
  );
}
