import { Button, Stack, Typography } from "@mui/material";

import { useActiveProject } from "@/hooks/useActiveProject";
import { cms3Descriptor } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";
import { DescriptorForm } from "@/organisms/DescriptorForm";
import { LogsTabs } from "@/pages/project/logs/LogsTabs";

export function SchemaPage() {
  const project = useActiveProject();
  if (!project) {
    return <Typography>Project not found.</Typography>;
  }

  return (
    <>
      <PageHeader
        title="Schema & Descriptor"
        subtitle={`Current descriptor: ${project.descriptorVersion}. Read-only view; re-profile to edit.`}
        actions={
          <Stack direction="row" spacing={1}>
            <Button size="small" variant="outlined" disabled>
              Version history
            </Button>
            <Button size="small" variant="contained" disabled>
              Re-profile sample
            </Button>
          </Stack>
        }
      />
      <LogsTabs />
      <DescriptorForm descriptor={cms3Descriptor} readOnly />
    </>
  );
}
