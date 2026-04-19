import { type Project } from "@/interfaces/domain";

export const projects: Project[] = [
  {
    id: "proj_cms3",
    orgId: "org_acme",
    slug: "cms3",
    name: "CMS3",
    description: "CMS agent journey orchestration engine",
    icon: "🧭",
    color: "#10b981",
    connectorStatus: "healthy",
    lastSyncIso: "2026-04-19T09:42:00Z",
    eventsLast24h: 842_310,
    evalScore: 0.88,
    evalTrend: 0.02,
    driftAlerts: 0,
    descriptorVersion: "v3",
    pineconeNamespace: "org_acme_cms3",
    createdAtIso: "2026-01-14T10:00:00Z",
  },
  {
    id: "proj_voyager",
    orgId: "org_acme",
    slug: "voyager",
    name: "Voyager",
    description: "Booking flow orchestrator",
    icon: "🚀",
    color: "#3b82f6",
    connectorStatus: "warning",
    lastSyncIso: "2026-04-19T05:11:00Z",
    eventsLast24h: 312_004,
    evalScore: 0.81,
    evalTrend: -0.01,
    driftAlerts: 1,
    descriptorVersion: "v1",
    pineconeNamespace: "org_acme_voyager",
    createdAtIso: "2026-03-02T10:00:00Z",
  },
  {
    id: "proj_payments",
    orgId: "org_acme",
    slug: "payments",
    name: "Payments Service",
    description: "Card + wallet payments pipeline",
    icon: "💳",
    color: "#f59e0b",
    connectorStatus: "failed",
    lastSyncIso: "2026-04-18T22:00:00Z",
    eventsLast24h: 0,
    evalScore: 0,
    evalTrend: 0,
    driftAlerts: 0,
    descriptorVersion: "v0",
    pineconeNamespace: "org_acme_payments",
    createdAtIso: "2026-04-12T10:00:00Z",
  },
];

export function findProject(orgSlug: string, projectSlug: string): Project | undefined {
  return projects.find(
    (p) => p.slug === projectSlug && p.orgId.endsWith(orgSlug.replace(/^org_/, "")),
  );
}

export function projectsForOrg(orgSlug: string): Project[] {
  const prefix = `org_${orgSlug}`;
  return projects.filter((p) => p.orgId === prefix);
}
