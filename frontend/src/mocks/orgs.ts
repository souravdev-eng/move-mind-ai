import { type Org } from "@/interfaces/domain";

export const orgs: Org[] = [
  {
    id: "org_acme",
    slug: "acme",
    name: "Acme Engineering",
    memberCount: 24,
    plan: "team",
  },
  {
    id: "org_nebula",
    slug: "nebula",
    name: "Nebula Labs",
    memberCount: 8,
    plan: "trial",
  },
];

export const defaultOrgSlug = "acme";
