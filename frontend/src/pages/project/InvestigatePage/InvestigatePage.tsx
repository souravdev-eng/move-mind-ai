import SendIcon from "@mui/icons-material/Send";
import { Box, Button, IconButton, Stack, TextField, Typography } from "@mui/material";

import { PageHeader } from "@/molecules/PageHeader";
import { EvidenceDrawer } from "@/organisms/EvidenceDrawer";
import { MessageList } from "@/organisms/MessageList";
import { ScopePanel } from "@/organisms/ScopePanel";

import { useInvestigatePage } from "./InvestigatePage.hook";

const SUGGESTIONS = [
  "Why is CID 7093495 stuck on step 4?",
  "Show all journeys that failed on step_order=3 today",
  "Did gql_createLead regress after deploy 4.12?",
];

export function InvestigatePage() {
  const {
    project,
    input,
    setInput,
    mode,
    setMode,
    correlationKey,
    setCorrelationKey,
    timeWindow,
    setTimeWindow,
    messages,
    streaming,
    reset,
    onSubmit,
    hasMessages,
    evidence,
  } = useInvestigatePage();
  const showEvidence = hasMessages;

  if (!project) {
    return <Typography>Project not found.</Typography>;
  }

  return (
    <>
      <PageHeader
        title="Investigate"
        subtitle={`Ask a question about ${project.name}. The agent will search logs and code.`}
        actions={
          hasMessages ? (
            <Button
              size="small"
              variant="outlined"
              onClick={() => {
                reset();
                setInput("");
              }}
            >
              New conversation
            </Button>
          ) : undefined
        }
      />

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            md: showEvidence ? "240px 1fr 320px" : "240px 1fr",
          },
          gap: 0,
          border: 1,
          borderColor: "divider",
          borderRadius: 1,
          minHeight: 560,
          bgcolor: "background.default",
        }}
      >
        <ScopePanel
          mode={mode}
          onModeChange={setMode}
          correlationKey={correlationKey}
          onCorrelationKeyChange={setCorrelationKey}
          timeWindow={timeWindow}
          onTimeWindowChange={setTimeWindow}
        />

        <Box sx={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
          <Box sx={{ flex: 1, overflowY: "auto", px: 3 }}>
            {!hasMessages ? (
              <Stack spacing={2} mt={4}>
                <Typography variant="subtitle1" fontWeight={600}>
                  Suggested questions
                </Typography>
                <Stack spacing={1}>
                  {SUGGESTIONS.map((s) => (
                    <Button
                      key={s}
                      variant="outlined"
                      sx={{ justifyContent: "flex-start", textTransform: "none" }}
                      onClick={() => {
                        setInput(s);
                      }}
                    >
                      {s}
                    </Button>
                  ))}
                </Stack>
              </Stack>
            ) : (
              <MessageList messages={messages} streaming={streaming} />
            )}
          </Box>

          <Box
            component="form"
            onSubmit={onSubmit}
            sx={{ borderTop: 1, borderColor: "divider", p: 2 }}
          >
            <Stack direction="row" spacing={1}>
              <TextField
                size="small"
                fullWidth
                placeholder="Ask a question about your logs…"
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                }}
                slotProps={{ htmlInput: { "aria-label": "Question input" } }}
              />
              <IconButton
                type="submit"
                color="primary"
                aria-label="Send"
                disabled={input.trim() === "" || streaming}
              >
                <SendIcon />
              </IconButton>
            </Stack>
          </Box>
        </Box>

        {showEvidence ? <EvidenceDrawer items={evidence} /> : null}
      </Box>
    </>
  );
}
