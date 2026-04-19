import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid2 as Grid,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
} from "@mui/material";

import { cms3Descriptor } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";
import { DescriptorForm } from "@/organisms/DescriptorForm";

import { useOnboardingWizard } from "./OnboardingWizard.hook";

const CONNECTORS: { id: string; name: string; status: "Available" | "Beta" | "Coming soon" }[] = [
  { id: "file_upload", name: "File upload", status: "Available" },
  { id: "s3", name: "Amazon S3", status: "Available" },
  { id: "webhook", name: "Webhook", status: "Available" },
  { id: "cloudwatch", name: "CloudWatch", status: "Beta" },
  { id: "datadog", name: "Datadog", status: "Coming soon" },
  { id: "elastic", name: "Elastic", status: "Coming soon" },
];

export function OnboardingWizard() {
  const { orgSlug, nav, active, form, setForm, next, back, steps: STEPS } = useOnboardingWizard();

  return (
    <>
      <PageHeader
        title="Create project"
        subtitle="Connect a log source, review the auto-detected descriptor, and go live."
      />

      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={active} alternativeLabel>
          {STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent sx={{ minHeight: 360 }}>
          {active === 0 ? (
            <Stack spacing={2} maxWidth={480}>
              <Typography variant="subtitle1" fontWeight={600}>
                Project basics
              </Typography>
              <TextField
                size="small"
                label="Project name"
                value={form.name}
                onChange={(e) => {
                  setForm({ ...form, name: e.target.value });
                }}
              />
              <TextField
                size="small"
                label="Slug"
                value={form.slug}
                onChange={(e) => {
                  setForm({ ...form, slug: e.target.value });
                }}
              />
              <TextField
                size="small"
                label="Short description"
                multiline
                minRows={2}
                value={form.description}
                onChange={(e) => {
                  setForm({ ...form, description: e.target.value });
                }}
              />
            </Stack>
          ) : null}

          {active === 1 ? (
            <>
              <Typography variant="subtitle1" fontWeight={600} mb={2}>
                Choose a log source
              </Typography>
              <Grid container spacing={2}>
                {CONNECTORS.map((c) => (
                  <Grid key={c.id} size={{ xs: 12, sm: 6, md: 4 }}>
                    <Card
                      variant="outlined"
                      onClick={() => {
                        if (c.status !== "Coming soon") {
                          setForm({ ...form, connector: c.id });
                        }
                      }}
                      sx={{
                        cursor: c.status === "Coming soon" ? "not-allowed" : "pointer",
                        opacity: c.status === "Coming soon" ? 0.6 : 1,
                        borderColor: form.connector === c.id ? "primary.main" : "divider",
                      }}
                    >
                      <CardContent>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Typography variant="subtitle2" fontWeight={600}>
                            {c.name}
                          </Typography>
                          <Chip
                            size="small"
                            label={c.status}
                            color={c.status === "Available" ? "success" : "default"}
                            variant="outlined"
                          />
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </>
          ) : null}

          {active === 2 ? (
            <Stack spacing={2} maxWidth={480}>
              <Typography variant="subtitle1" fontWeight={600}>
                Configure {form.connector}
              </Typography>
              <TextField
                size="small"
                label="Bucket / endpoint"
                value={form.bucket}
                onChange={(e) => {
                  setForm({ ...form, bucket: e.target.value });
                }}
              />
              <TextField
                size="small"
                select
                label="Region"
                value={form.region}
                onChange={(e) => {
                  setForm({ ...form, region: e.target.value });
                }}
              >
                <MenuItem value="us-east-1">us-east-1</MenuItem>
                <MenuItem value="us-west-2">us-west-2</MenuItem>
                <MenuItem value="eu-west-1">eu-west-1</MenuItem>
              </TextField>
              <Button size="small" variant="outlined" sx={{ alignSelf: "flex-start" }}>
                Test connection
              </Button>
            </Stack>
          ) : null}

          {active === 3 ? (
            <Stack spacing={2}>
              <Typography variant="subtitle1" fontWeight={600}>
                Pulling sample (200–1000 events)
              </Typography>
              <LinearProgress variant="determinate" value={72} sx={{ height: 6, borderRadius: 3 }} />
              <Typography variant="caption" color="text.secondary">
                720 / 1000 events fetched…
              </Typography>
            </Stack>
          ) : null}

          {active === 4 ? (
            <>
              <Typography variant="subtitle1" fontWeight={600} mb={1}>
                Profiler review
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={3}>
                Confidence indicators show how certain the profiler is about each field. Override
                anything that looks wrong.
              </Typography>
              <DescriptorForm descriptor={cms3Descriptor} />
            </>
          ) : null}

          {active === 5 ? (
            <Stack spacing={2}>
              <Typography variant="subtitle1" fontWeight={600}>
                Confirm & kick off ingestion
              </Typography>
              <Typography variant="body2" color="text.secondary" maxWidth={560}>
                We&apos;ll run the full ingestion in the background. You can close this tab and
                come back to the project from the dashboard.
              </Typography>
              <Box>
                <Chip label={`Connector: ${form.connector}`} sx={{ mr: 1 }} />
                <Chip label={`Region: ${form.region}`} sx={{ mr: 1 }} />
                <Chip label="Descriptor v1 (auto)" />
              </Box>
            </Stack>
          ) : null}

          {active === 6 ? (
            <Stack spacing={2}>
              <Typography variant="subtitle1" fontWeight={600}>
                You&apos;re live 🎉
              </Typography>
              <Typography variant="body2" color="text.secondary" maxWidth={560}>
                Ingestion is running. Your project is ready to answer questions — we&apos;ve
                landed you on the reference project for now so you can see what it looks like.
              </Typography>
              <Button
                variant="contained"
                size="small"
                sx={{ alignSelf: "flex-start" }}
                onClick={() => {
                  nav(`/orgs/${orgSlug}/projects/cms3/investigate`);
                }}
              >
                Start investigating
              </Button>
            </Stack>
          ) : null}
        </CardContent>
      </Card>

      <Stack direction="row" justifyContent="space-between">
        <Button disabled={active === 0} onClick={back}>
          Back
        </Button>
        <Button
          variant="contained"
          onClick={next}
          disabled={active === STEPS.length - 1}
        >
          {active === STEPS.length - 2 ? "Kick off ingestion" : "Next"}
        </Button>
      </Stack>
    </>
  );
}
