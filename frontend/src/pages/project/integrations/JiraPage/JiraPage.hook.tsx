import { useState } from "react";

import { useActiveProject } from "@/hooks/useActiveProject";
import { jiraConfigs, jiraTickets } from "@/mocks";

export type TabKey = "connect" | "mapping" | "activity";

export function useJiraPage() {
  const project = useActiveProject();
  const [tab, setTab] = useState<TabKey>("connect");
  const config = project ? jiraConfigs.find((c) => c.projectId === project.id) : undefined;
  const tickets = project ? jiraTickets.filter((t) => t.projectId === project.id) : [];

  return { project, tab, setTab, config, tickets };
}
