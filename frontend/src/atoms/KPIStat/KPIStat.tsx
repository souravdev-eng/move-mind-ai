import { Card, CardContent, Stack, Typography } from "@mui/material";

interface Props {
  label: string;
  value: string;
  delta?: string;
  deltaPositive?: boolean;
}

export function KPIStat({ label, value, delta, deltaPositive }: Props) {
  return (
    <Card variant="outlined" sx={{ minWidth: 180, flex: 1 }}>
      <CardContent>
        <Typography variant="caption" color="text.secondary">
          {label}
        </Typography>
        <Stack direction="row" alignItems="baseline" spacing={1} mt={0.5}>
          <Typography variant="h5" component="div" fontWeight={600}>
            {value}
          </Typography>
          {delta ? (
            <Typography
              variant="caption"
              color={deltaPositive ? "success.main" : "error.main"}
              fontWeight={500}
            >
              {delta}
            </Typography>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
