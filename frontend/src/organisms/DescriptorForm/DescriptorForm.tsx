import { type ReactNode } from "react";

import { Box, Chip, Grid2 as Grid, Stack, TextField, Typography } from "@mui/material";

import { type Descriptor } from "@/interfaces/domain";
import { DescriptorField } from "@/molecules/DescriptorField";

interface Props {
  descriptor: Descriptor;
  readOnly?: boolean;
}

export function DescriptorForm({ descriptor, readOnly = false }: Props) {
  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 7 }}>
        <Stack spacing={3}>
          <Section title="Identity">
            <TextField
              size="small"
              label="Domain ID"
              value={descriptor.domainId}
              slotProps={{ input: { readOnly } }}
              fullWidth
            />
            <TextField
              size="small"
              label="Display name"
              value={descriptor.displayName}
              slotProps={{ input: { readOnly } }}
              fullWidth
            />
          </Section>

          <Section title="Correlation & grouping">
            <DescriptorField
              label="Primary correlation key"
              field={descriptor.correlationKeys.primary}
              readOnly={readOnly}
            />
            <DescriptorField
              label="Secondary correlation key"
              field={descriptor.correlationKeys.secondary}
              readOnly={readOnly}
            />
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {descriptor.groupBy.map((g) => (
                <Chip key={g} size="small" label={`group_by: ${g}`} />
              ))}
            </Stack>
          </Section>

          <Section title="Identifiers">
            <DescriptorField label="Actor" field={descriptor.identifiers.actor} readOnly={readOnly} />
            <DescriptorField label="Flow" field={descriptor.identifiers.flow} readOnly={readOnly} />
            <DescriptorField label="Unit" field={descriptor.identifiers.unit} readOnly={readOnly} />
            <DescriptorField
              label="Location"
              field={descriptor.identifiers.location}
              readOnly={readOnly}
            />
          </Section>

          <Section title="Timing & levels">
            <DescriptorField
              label="Timestamp field"
              field={descriptor.timestampField}
              readOnly={readOnly}
            />
            <DescriptorField
              label="Level field"
              field={descriptor.levelField}
              readOnly={readOnly}
            />
            <DescriptorField
              label="Message field"
              field={descriptor.messageField}
              readOnly={readOnly}
            />
          </Section>

          <Section title="Error signals">
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {descriptor.errorSignals.fields.map((f) => (
                <Chip key={f} size="small" label={f} />
              ))}
            </Stack>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {descriptor.errorSignals.levelValues.map((v) => (
                <Chip key={v} size="small" color="error" variant="outlined" label={v} />
              ))}
            </Stack>
          </Section>

          <Section title="Vocabulary">
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Chip size="small" label={`event: ${descriptor.vocabulary.eventUnit}`} />
              <Chip size="small" label={`flow: ${descriptor.vocabulary.flowUnit}`} />
              <Chip size="small" label={`actor: ${descriptor.vocabulary.actorUnit}`} />
              <Chip size="small" label={`routing: ${descriptor.vocabulary.routingUnit}`} />
            </Stack>
          </Section>

          <Section title="Known patterns">
            <Stack spacing={1}>
              {descriptor.knownPatterns.map((p, i) => (
                <Typography key={String(i)} variant="body2" color="text.secondary">
                  • {p}
                </Typography>
              ))}
            </Stack>
          </Section>

          <Section title="Domain description">
            <TextField
              size="small"
              value={descriptor.domainDescription}
              slotProps={{ input: { readOnly } }}
              multiline
              minRows={3}
              fullWidth
            />
          </Section>
        </Stack>
      </Grid>

      <Grid size={{ xs: 12, md: 5 }}>
        <Box
          sx={{
            position: "sticky",
            top: 88,
            border: 1,
            borderColor: "divider",
            borderRadius: 1,
            p: 2,
            bgcolor: "background.paper",
          }}
        >
          <Typography variant="subtitle2" fontWeight={600} mb={1}>
            Live preview — one execution group
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Reconstructed from the current descriptor.
          </Typography>
          <Box
            component="pre"
            sx={{
              mt: 1.5,
              p: 1.5,
              bgcolor: "action.hover",
              borderRadius: 1,
              fontFamily: "monospace",
              fontSize: 12,
              overflowX: "auto",
              whiteSpace: "pre-wrap",
            }}
          >
{`execution_id: exec_5521
customer_id: 7093495
journey_id: jrny_onboarding_v3
events:
  - step_order: 1  page_path: /onboard/start   level: info
  - step_order: 2  page_path: /onboard/name    level: info
  - step_order: 3  page_path: /onboard/confirm level: info
  - step_order: 4  page_path: /onboard/confirm level: error
    error_code: E_COND_NULL
    error_message: "actor undefined"
`}
          </Box>
        </Box>
      </Grid>
    </Grid>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Box>
      <Typography variant="overline" color="text.secondary">
        {title}
      </Typography>
      <Stack spacing={1.5} mt={0.5}>
        {children}
      </Stack>
    </Box>
  );
}
