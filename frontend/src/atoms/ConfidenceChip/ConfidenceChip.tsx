import { Chip, Tooltip } from "@mui/material";

interface Props {
  confidence: "high" | "medium" | "low";
  source?: string;
}

const colorMap = {
  high: "success",
  medium: "warning",
  low: "error",
} as const;

const labelMap = {
  high: "High",
  medium: "Medium",
  low: "Low",
} as const;

export function ConfidenceChip({ confidence, source }: Props) {
  const chip = (
    <Chip
      size="small"
      variant="outlined"
      color={colorMap[confidence]}
      label={`${labelMap[confidence]} confidence`}
    />
  );
  return source ? (
    <Tooltip title={source}>
      <span>{chip}</span>
    </Tooltip>
  ) : (
    chip
  );
}
