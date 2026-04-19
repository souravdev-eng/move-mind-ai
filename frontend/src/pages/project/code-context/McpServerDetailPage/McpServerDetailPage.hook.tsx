import { useState } from "react";

import { useNavigate, useParams } from "react-router-dom";

import { mcpServers } from "@/mocks";

export type TabKey = "tools" | "resources" | "invocations" | "health";

export function useMcpServerDetailPage() {
  const { orgSlug = "acme", projectSlug = "", serverId } = useParams();
  const nav = useNavigate();
  const [tab, setTab] = useState<TabKey>("tools");
  const server = mcpServers.find((s) => s.id === serverId);
  const backTo = `/orgs/${orgSlug}/projects/${projectSlug}/code-context/mcp`;

  return { tab, setTab, server, nav, backTo };
}
