import { type JiraConfig, type JiraTicket } from "@/interfaces/domain";

export const jiraConfigs: JiraConfig[] = [
  {
    projectId: "proj_cms3",
    connected: true,
    site: "acme.atlassian.net",
    jiraProjectKey: "CMS",
    defaultIssueType: "Bug",
    defaultPriority: "High",
    managerTriggeredOnly: true,
  },
  {
    projectId: "proj_voyager",
    connected: false,
    site: "",
    jiraProjectKey: "",
    defaultIssueType: "Bug",
    defaultPriority: "Medium",
    managerTriggeredOnly: true,
  },
];

export const jiraTickets: JiraTicket[] = [
  {
    id: "tk_01",
    projectId: "proj_cms3",
    key: "CMS-4821",
    title: "CID 7093495 stuck on step 4 — condition evaluator null ref",
    verdict: "bug",
    createdAtIso: "2026-04-19T08:22:00Z",
    status: "in_progress",
    assignee: "ana@acme.io",
    url: "https://acme.atlassian.net/browse/CMS-4821",
  },
  {
    id: "tk_02",
    projectId: "proj_cms3",
    key: "CMS-4810",
    title: "gql_createLead 500s after deploy 4.12",
    verdict: "bug",
    createdAtIso: "2026-04-18T12:00:00Z",
    status: "open",
    assignee: "priya@acme.io",
    url: "https://acme.atlassian.net/browse/CMS-4810",
  },
];
