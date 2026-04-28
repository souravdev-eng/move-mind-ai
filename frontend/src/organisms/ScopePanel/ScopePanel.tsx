import {
  Box,
  Chip,
  MenuItem,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";

import { type ExplanationMode } from "@/interfaces/domain";

interface Props {
  mode: ExplanationMode;
  onModeChange: (mode: ExplanationMode) => void;
  correlationKey: string;
  onCorrelationKeyChange: (value: string) => void;
  timeWindow: string;
  onTimeWindowChange: (value: string) => void;
}

export function ScopePanel({
  mode,
  onModeChange,
  correlationKey,
  onCorrelationKeyChange,
  timeWindow,
  onTimeWindowChange,
}: Props) {
  return (
    <Box
      sx={{
        borderRight: 1,
        borderColor: "divider",
        bgcolor: "background.paper",
        p: 2,
      }}
    >
      <Typography variant="subtitle2" fontWeight={600} mb={1.5}>
        Scope
      </Typography>
      <Stack spacing={2}>
        <TextField
          size="small"
          label="Correlation key (e.g. CID)"
          value={correlationKey}
          onChange={(e) => {
            onCorrelationKeyChange(e.target.value);
          }}
        />
        <TextField
          size="small"
          select
          label="Time window"
          value={timeWindow}
          onChange={(e) => {
            onTimeWindowChange(e.target.value);
          }}
        >
          <MenuItem value="1h">Last 1h</MenuItem>
          <MenuItem value="24h">Last 24h</MenuItem>
          <MenuItem value="7d">Last 7d</MenuItem>
          <MenuItem value="30d">Last 30d</MenuItem>
        </TextField>
        <Box>
          <Typography variant="overline" color="text.secondary" display="block" mb={0.5}>
            Mode
          </Typography>
          <ToggleButtonGroup
            size="small"
            exclusive
            value={mode}
            onChange={(_e, v: ExplanationMode | null) => {
              if (v) {
                onModeChange(v);
              }
            }}
            fullWidth
          >
            <ToggleButton value="manager">Manager</ToggleButton>
            <ToggleButton value="developer">Developer</ToggleButton>
          </ToggleButtonGroup>
        </Box>
        <Box>
          <Typography variant="overline" color="text.secondary" display="block" mb={0.5}>
            Descriptor peek
          </Typography>
          <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
            <Chip size="small" label="domain: cms3" />
            <Chip size="small" label="primary: execution_id" />
            <Chip size="small" label="actor: customer_id" />
          </Stack>
        </Box>
      </Stack>
    </Box>
  );
}
