import { useState } from "react";

import { useActiveProject } from "@/hooks/useActiveProject";
import { type Verdict } from "@/interfaces/domain";
import { conversations } from "@/mocks";

export type VerdictFilter = Verdict | "all";

export function useConversationsPage() {
  const project = useActiveProject();
  const [query, setQuery] = useState("");
  const [verdict, setVerdict] = useState<VerdictFilter>("all");

  const filtered = project
    ? conversations
      .filter((c) => c.projectId === project.id)
      .filter((c) => (verdict === "all" ? true : c.verdict === verdict))
      .filter((c) =>
        query.trim() === ""
          ? true
          : `${c.title} ${c.preview} ${c.author}`.toLowerCase().includes(query.toLowerCase()),
      )
    : [];

  return { project, query, setQuery, verdict, setVerdict, filtered };
}
