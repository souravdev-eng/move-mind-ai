import { useState, type MouseEvent } from "react";

import { useNavigate, useParams } from "react-router-dom";

import { orgs } from "@/mocks";

export function useOrgSwitcher() {
  const { orgSlug } = useParams();
  const nav = useNavigate();
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);
  const current = orgs.find((o) => o.slug === orgSlug) ?? orgs[0];

  function open(e: MouseEvent<HTMLButtonElement>) {
    setAnchor(e.currentTarget);
  }
  function close() {
    setAnchor(null);
  }
  function selectOrg(slug: string) {
    setAnchor(null);
    nav(`/orgs/${slug}/dashboard`);
  }

  return { anchor, current, orgs, open, close, selectOrg };
}
