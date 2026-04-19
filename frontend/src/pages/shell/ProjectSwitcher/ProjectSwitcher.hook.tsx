import { useState, type MouseEvent } from "react";

import { useLocation, useNavigate, useParams } from "react-router-dom";

import { projectsForOrg } from "@/mocks";

function currentSection(pathname: string): string {
  const match = /\/projects\/[^/]+\/([^/]+(?:\/[^/]+)?)/.exec(pathname);
  return match ? (match[1] ?? "overview") : "overview";
}

export function useProjectSwitcher() {
  const { orgSlug, projectSlug } = useParams();
  const { pathname } = useLocation();
  const nav = useNavigate();
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);
  const list = projectsForOrg(orgSlug ?? "acme");
  const current = list.find((p) => p.slug === projectSlug);

  function open(e: MouseEvent<HTMLButtonElement>) {
    setAnchor(e.currentTarget);
  }
  function close() {
    setAnchor(null);
  }
  function selectProject(slug: string) {
    setAnchor(null);
    const section = current ? currentSection(pathname) : "overview";
    nav(`/orgs/${orgSlug ?? "acme"}/projects/${slug}/${section}`);
  }

  return { anchor, current, list, open, close, selectProject };
}
