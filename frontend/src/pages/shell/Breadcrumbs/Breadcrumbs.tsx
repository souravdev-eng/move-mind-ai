import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { Box, Link, Stack, Typography } from "@mui/material";
import { Link as RouterLink, useLocation, useParams } from "react-router-dom";

import { orgs, projects } from "@/mocks";

interface Crumb {
  label: string;
  to?: string;
}

function buildCrumbs(pathname: string, params: Record<string, string | undefined>): Crumb[] {
  const { orgSlug, projectSlug, serverId } = params;
  const crumbs: Crumb[] = [];
  const org = orgs.find((o) => o.slug === orgSlug);
  if (org) {
    crumbs.push({ label: org.name, to: `/orgs/${org.slug}/dashboard` });
  }
  if (projectSlug) {
    const project = projects.find((p) => p.slug === projectSlug);
    if (project) {
      crumbs.push({
        label: project.name,
        to: `/orgs/${orgSlug ?? "acme"}/projects/${project.slug}/overview`,
      });
    }
  }
  const segments = pathname.split("/").filter(Boolean);
  const lastTwo = segments.slice(-2);
  const labelMap: Record<string, string> = {
    dashboard: "Dashboard",
    overview: "Overview",
    investigate: "Investigate",
    conversations: "Conversations",
    logs: "Logs",
    connectors: "Connectors",
    runs: "Ingestion runs",
    schema: "Schema & Descriptor",
    integrations: "Integrations",
    jira: "Jira",
    notion: "Notion",
    slack: "Slack",
    webhooks: "Webhooks",
    "code-context": "Code Context",
    mcp: "MCP Servers",
    settings: "Settings",
    onboarding: "Onboarding",
    evaluations: "Evaluations",
    billing: "Billing",
  };
  lastTwo.forEach((seg) => {
    const label = labelMap[seg];
    if (label && !crumbs.some((c) => c.label === label)) {
      crumbs.push({ label });
    }
  });
  if (serverId && !crumbs.some((c) => c.label.startsWith("Server"))) {
    crumbs.push({ label: `Server ${serverId}` });
  }
  return crumbs;
}

export function Breadcrumbs() {
  const { pathname } = useLocation();
  const params = useParams();
  const crumbs = buildCrumbs(pathname, params);
  if (crumbs.length === 0) {
    return null;
  }
  return (
    <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mb: 2, flexWrap: "wrap" }}>
      {crumbs.map((c, i) => (
        <Box key={`${c.label}-${String(i)}`} sx={{ display: "flex", alignItems: "center" }}>
          {i > 0 ? (
            <ChevronRightIcon fontSize="small" sx={{ color: "text.disabled", mx: 0.25 }} />
          ) : null}
          {c.to && i < crumbs.length - 1 ? (
            <Link
              component={RouterLink}
              to={c.to}
              underline="hover"
              color="text.secondary"
              variant="body2"
            >
              {c.label}
            </Link>
          ) : (
            <Typography
              variant="body2"
              color={i === crumbs.length - 1 ? "text.primary" : "text.secondary"}
            >
              {c.label}
            </Typography>
          )}
        </Box>
      ))}
    </Stack>
  );
}
