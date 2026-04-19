import { useParams } from "react-router-dom";

import { SectionTabs } from "@/molecules/SectionTabs";

export function LogsTabs() {
  const { orgSlug = "acme", projectSlug = "" } = useParams();
  const base = `/orgs/${orgSlug}/projects/${projectSlug}/logs`;
  return (
    <SectionTabs
      tabs={[
        { label: "Connectors", to: `${base}/connectors` },
        { label: "Ingestion runs", to: `${base}/runs` },
        { label: "Schema & Descriptor", to: `${base}/schema` },
      ]}
    />
  );
}
