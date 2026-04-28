import { Navigate, createBrowserRouter, type RouteObject } from "react-router-dom";

import { ComingSoonPage } from "./pages/ComingSoonPage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { OnboardingWizard } from "./pages/onboarding/OnboardingWizard";
import { McpServerDetailPage } from "./pages/project/code-context/McpServerDetailPage";
import { McpServersPage } from "./pages/project/code-context/McpServersPage";
import { ConversationsPage } from "./pages/project/ConversationsPage";
import { IntegrationsHub } from "./pages/project/integrations/IntegrationsHub";
import { JiraPage } from "./pages/project/integrations/JiraPage";
import { InvestigatePage } from "./pages/project/InvestigatePage";
import { ConnectorsPage } from "./pages/project/logs/ConnectorsPage";
import { IngestionRunsPage } from "./pages/project/logs/IngestionRunsPage";
import { SchemaPage } from "./pages/project/logs/SchemaPage";
import { OverviewPage } from "./pages/project/OverviewPage";
import { SettingsPage } from "./pages/project/SettingsPage";
import { AppShell } from "./pages/shell/AppShell";

export const routeDefinitions: RouteObject[] = [
  {
    path: "/",
    element: <Navigate to="/orgs/acme/dashboard" replace />,
  },
  {
    path: "/orgs/:orgSlug",
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="dashboard" replace /> },
      { path: "dashboard", element: <DashboardPage /> },
      { path: "onboarding", element: <OnboardingWizard /> },
      { path: "onboarding/:step", element: <OnboardingWizard /> },
      { path: "integrations", element: <ComingSoonPage title="Organisation Integrations" /> },
      { path: "members", element: <ComingSoonPage title="Members & Roles" /> },
      { path: "billing", element: <ComingSoonPage title="Billing & Usage" /> },
      {
        path: "projects/:projectSlug",
        children: [
          { index: true, element: <Navigate to="overview" replace /> },
          { path: "overview", element: <OverviewPage /> },
          { path: "investigate", element: <InvestigatePage /> },
          { path: "conversations", element: <ConversationsPage /> },
          {
            path: "logs",
            children: [
              { index: true, element: <Navigate to="connectors" replace /> },
              { path: "connectors", element: <ConnectorsPage /> },
              { path: "runs", element: <IngestionRunsPage /> },
              { path: "schema", element: <SchemaPage /> },
            ],
          },
          {
            path: "integrations",
            children: [
              { index: true, element: <IntegrationsHub /> },
              { path: "jira", element: <JiraPage /> },
              { path: "notion", element: <ComingSoonPage title="Notion Integration" /> },
              { path: "slack", element: <ComingSoonPage title="Slack Integration" /> },
              { path: "webhooks", element: <ComingSoonPage title="Outbound Webhooks" /> },
            ],
          },
          {
            path: "code-context",
            children: [
              { index: true, element: <Navigate to="mcp" replace /> },
              { path: "mcp", element: <McpServersPage /> },
              { path: "mcp/:serverId", element: <McpServerDetailPage /> },
              { path: "repo-index", element: <ComingSoonPage title="Hosted Repo Index" /> },
            ],
          },
          { path: "evaluations", element: <ComingSoonPage title="Evaluations" /> },
          { path: "settings", element: <SettingsPage /> },
        ],
      },
    ],
  },
];

export const router = createBrowserRouter(routeDefinitions);
