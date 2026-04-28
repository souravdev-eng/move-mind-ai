import { useParams } from "react-router-dom";

import { type Project } from "@/interfaces/domain";
import { projects } from "@/mocks";

export function useActiveProject(): Project | undefined {
  const { projectSlug } = useParams();
  return projects.find((p) => p.slug === projectSlug);
}

export function useRouteParams(): { orgSlug: string; projectSlug: string | undefined } {
  const { orgSlug, projectSlug } = useParams();
  return { orgSlug: orgSlug ?? "acme", projectSlug };
}
