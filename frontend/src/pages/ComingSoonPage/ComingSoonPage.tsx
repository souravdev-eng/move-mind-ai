import ConstructionIcon from "@mui/icons-material/Construction";
import { Card, CardContent } from "@mui/material";

import { EmptyState } from "@/molecules/EmptyState";
import { PageHeader } from "@/molecules/PageHeader";

export function ComingSoonPage({ title }: { title: string }) {
  return (
    <>
      <PageHeader title={title} subtitle="Planned for a fast-follow ship — see SOW §7 phasing." />
      <Card variant="outlined">
        <CardContent>
          <EmptyState
            icon={<ConstructionIcon fontSize="large" />}
            title="Coming soon"
            description="This page is scoped but not yet built. Ping @saurav if you need it prioritised."
          />
        </CardContent>
      </Card>
    </>
  );
}
