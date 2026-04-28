import { Chip } from "@mui/material";

import {
  type ConnectorStatus,
  type McpStatus,
  type RunStatus,
  type Verdict,
} from "@/interfaces/domain";

type Status = ConnectorStatus | McpStatus | RunStatus | Verdict | "open" | "in_progress" | "done";

const colorMap: Record<Status, "default" | "success" | "warning" | "error" | "info"> = {
  healthy: "success",
  connected: "success",
  succeeded: "success",
  done: "success",
  bug: "error",
  failed: "error",
  error: "error",
  warning: "warning",
  partial: "warning",
  handshaking: "info",
  running: "info",
  in_progress: "info",
  open: "default",
  paused: "default",
  disabled: "default",
  business_condition: "info",
  unknown: "default",
};

const labelMap: Record<Status, string> = {
  healthy: "Healthy",
  connected: "Connected",
  succeeded: "Succeeded",
  done: "Done",
  bug: "Bug",
  failed: "Failed",
  error: "Error",
  warning: "Warning",
  partial: "Partial",
  handshaking: "Handshaking",
  running: "Running",
  in_progress: "In progress",
  open: "Open",
  paused: "Paused",
  disabled: "Disabled",
  business_condition: "Business condition",
  unknown: "Unknown",
};

export function StatusBadge({ status }: { status: Status }) {
  const isUnknown = status === "unknown";
  return (
    <Chip
      size="small"
      variant={isUnknown ? "filled" : "outlined"}
      color={colorMap[status]}
      label={labelMap[status]}
      sx={isUnknown ? { opacity: 0.6, fontStyle: "italic" } : {}}
    />
  );
}
