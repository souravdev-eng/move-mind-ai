import {
  Box,
  Button,
  Card,
  CardContent,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";

import { useActiveProject } from "@/hooks/useActiveProject";
import { members } from "@/mocks";
import { PageHeader } from "@/molecules/PageHeader";

export function SettingsPage() {
  const project = useActiveProject();
  if (!project) {
    return <Typography>Project not found.</Typography>;
  }

  return (
    <>
      <PageHeader title="Project settings" subtitle="Members, retention and danger zone." />

      <Stack spacing={3}>
        <Card variant="outlined">
          <CardContent>
            <Stack direction="row" justifyContent="space-between" mb={1.5}>
              <Typography variant="subtitle1" fontWeight={600}>
                Members
              </Typography>
              <Button size="small" variant="outlined">
                Invite teammate
              </Button>
            </Stack>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Joined</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {members.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell>{m.name}</TableCell>
                    <TableCell>{m.email}</TableCell>
                    <TableCell>{m.role}</TableCell>
                    <TableCell>
                      {formatDistanceToNowStrict(new Date(m.joinedAtIso), { addSuffix: true })}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} mb={1.5}>
              Retention
            </Typography>
            <Stack spacing={2} maxWidth={480}>
              <TextField size="small" select label="Conversation retention" defaultValue="90">
                <MenuItem value="30">30 days</MenuItem>
                <MenuItem value="90">90 days</MenuItem>
                <MenuItem value="365">365 days</MenuItem>
              </TextField>
              <TextField size="small" select label="Raw log retention" defaultValue="14">
                <MenuItem value="7">7 days</MenuItem>
                <MenuItem value="14">14 days</MenuItem>
                <MenuItem value="30">30 days</MenuItem>
              </TextField>
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined" sx={{ borderColor: "error.main" }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} color="error.main" mb={1.5}>
              Danger zone
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Button variant="outlined">Re-profile descriptor</Button>
              <Button variant="outlined">Rotate Pinecone namespace</Button>
              <Box sx={{ flexGrow: 1 }} />
              <Button color="error" variant="outlined">
                Delete project
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </>
  );
}
