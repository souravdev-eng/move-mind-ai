import { Stack, TextField, Typography } from "@mui/material";

import { ConfidenceChip } from "@/atoms/ConfidenceChip";
import { type DescriptorFieldValue } from "@/interfaces/domain";

interface Props {
  label: string;
  field: DescriptorFieldValue;
  readOnly?: boolean;
  onChange?: (value: string) => void;
}

export function DescriptorField({ label, field, readOnly = false, onChange }: Props) {
  return (
    <Stack spacing={0.5}>
      <Stack direction="row" alignItems="center" spacing={1}>
        <Typography variant="body2" fontWeight={500}>
          {label}
        </Typography>
        <ConfidenceChip confidence={field.confidence} source={field.source} />
        {field.editedByUser ? (
          <Typography variant="caption" color="text.secondary">
            · edited
          </Typography>
        ) : null}
      </Stack>
      <TextField
        size="small"
        value={field.value}
        slotProps={{ input: { readOnly } }}
        onChange={(e) => {
          onChange?.(e.target.value);
        }}
        fullWidth
      />
    </Stack>
  );
}
