import { type McpServer } from "@/interfaces/domain";

export const mcpServers: McpServer[] = [
  {
    id: "mcp_cms3_repo",
    projectId: "proj_cms3",
    name: "acme/cms3 code server",
    transport: "http",
    endpoint: "https://mcp.acme.io/cms3",
    status: "connected",
    lastHeartbeatIso: "2026-04-19T09:50:00Z",
    tools: [
      {
        name: "get_code_context",
        description: "Return the source of the function that emits a given log message.",
        inputSchema: "{ symbolOrFile: string }",
        callsLast24h: 47,
        writeCapable: false,
        whitelisted: true,
      },
      {
        name: "get_recent_changes",
        description: "Return recent commits touching a file.",
        inputSchema: "{ file: string; since: string }",
        callsLast24h: 12,
        writeCapable: false,
        whitelisted: true,
      },
      {
        name: "apply_patch",
        description: "Apply a patch to a file.",
        inputSchema: "{ file: string; patch: string }",
        callsLast24h: 0,
        writeCapable: true,
        whitelisted: false,
      },
    ],
    resources: [
      {
        uriTemplate: "repo://cms3/{path}",
        description: "Read a file from the CMS3 repo.",
        lastReadIso: "2026-04-19T09:02:00Z",
      },
    ],
    invocations: [
      {
        id: "inv_01",
        toolName: "get_code_context",
        inputPreview: '{ symbolOrFile: "evaluateCondition" }',
        outputPreview: "function evaluateCondition(ctx) { /* … */ }",
        latencyMs: 214,
        atIso: "2026-04-19T09:02:00Z",
        success: true,
      },
      {
        id: "inv_02",
        toolName: "get_recent_changes",
        inputPreview: '{ file: "src/graphql/createLead.ts", since: "7d" }',
        outputPreview: "3 commits, last by ana@ 2026-04-17",
        latencyMs: 98,
        atIso: "2026-04-19T08:40:00Z",
        success: true,
      },
    ],
  },
  {
    id: "mcp_voyager_repo",
    projectId: "proj_voyager",
    name: "acme/voyager code server",
    transport: "stdio",
    endpoint: "mcp-voyager --stdio",
    status: "handshaking",
    lastHeartbeatIso: "2026-04-19T09:48:00Z",
    tools: [],
    resources: [],
    invocations: [],
  },
];
