import { type ReactNode } from "react";

import ExtensionIcon from "@mui/icons-material/Extension";
import {
  Button,
  Card,
  CardActions,
  CardContent,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import { Link as RouterLink, useParams } from "react-router-dom";

import { StatusBadge } from "@/atoms/StatusBadge";
import { jiraConfigs } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";

interface IntegrationCardProps {
  name: string;
  pitch: string;
  category: string;
  to: string;
  status: ReactNode;
}

function IntegrationCard({ name, pitch, category, to, status }: IntegrationCardProps) {
  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      <CardContent>
        <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <ExtensionIcon fontSize="small" />
            <Typography variant="subtitle2" fontWeight={600}>
              {name}
            </Typography>
          </Stack>
          {status}
        </Stack>
        <Typography variant="caption" color="text.secondary">
          {category}
        </Typography>
        <Typography variant="body2" mt={1}>
          {pitch}
        </Typography>
      </CardContent>
      <CardActions>
        <Button size="small" component={RouterLink} to={to}>
          Open
        </Button>
      </CardActions>
    </Card>
  );
}

export function IntegrationsHub() {
  const { orgSlug = "acme", projectSlug = "" } = useParams();
  const base = `/orgs/${orgSlug}/projects/${projectSlug}/integrations`;
  const jiraConnected = jiraConfigs[0]?.connected === true;

  return (
    <>
      <PageHeader
        title="Integrations"
        subtitle="Connect MoveMind to your ticketing, docs and alerting tools."
      />
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <IntegrationCard
            name="Jira"
            category="Ticketing"
            pitch="Create Jira tickets from verdicts. Manager-triggered only."
            to={`${base}/jira`}
            status={
              jiraConnected ? <StatusBadge status="connected" /> : <StatusBadge status="disabled" />
            }
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <IntegrationCard
            name="Notion"
            category="Docs"
            pitch="Publish investigations to a Notion workspace."
            to={`${base}/notion`}
            status={<StatusBadge status="disabled" />}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <IntegrationCard
            name="Slack"
            category="Chat / alerting"
            pitch="Route verdicts to the right channel."
            to={`${base}/slack`}
            status={<StatusBadge status="disabled" />}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <IntegrationCard
            name="Outbound webhooks"
            category="Alerting"
            pitch="HMAC-signed POST on investigation.completed."
            to={`${base}/webhooks`}
            status={<StatusBadge status="disabled" />}
          />
        </Grid>
      </Grid>
    </>
  );
}
