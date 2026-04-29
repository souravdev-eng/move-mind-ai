export type Verdict = "bug" | "business_condition" | "unknown";

export type ConnectorKind =
  | "s3"
  | "cloudwatch"
  | "webhook"
  | "file_upload"
  | "datadog"
  | "elastic"
  | "kafka";

export type ConnectorStatus = "healthy" | "warning" | "failed" | "paused";

export type McpTransport = "stdio" | "http" | "sse";
export type McpStatus = "connected" | "handshaking" | "error" | "disabled";

export type RunStatus = "succeeded" | "partial" | "failed" | "running";

export type ExplanationMode = "manager" | "developer";

export interface Org {
  id: string;
  slug: string;
  name: string;
  memberCount: number;
  plan: "trial" | "team" | "enterprise";
}

export interface Project {
  id: string;
  orgId: string;
  slug: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  connectorStatus: ConnectorStatus;
  lastSyncIso: string;
  eventsLast24h: number;
  evalScore: number;
  evalTrend: number;
  driftAlerts: number;
  descriptorVersion: string;
  pineconeNamespace: string;
  createdAtIso: string;
}

export interface Connector {
  id: string;
  projectId: string;
  kind: ConnectorKind;
  name: string;
  status: ConnectorStatus;
  lastSyncIso: string;
  nextSyncIso: string | null;
  eventsLast24h: number;
  config: Record<string, string>;
  scheduleLabel: string;
}

export interface IngestionRun {
  id: string;
  projectId: string;
  connectorId: string;
  startedAtIso: string;
  durationMs: number;
  eventsIn: number;
  eventsOut: number;
  embedCostUsd: number;
  errorsCount: number;
  status: RunStatus;
}

export interface DescriptorFieldValue {
  value: string;
  confidence: "high" | "medium" | "low";
  source: string;
  editedByUser: boolean;
}

export interface Descriptor {
  domainId: string;
  displayName: string;
  version: string;
  correlationKeys: { primary: DescriptorFieldValue; secondary: DescriptorFieldValue };
  groupBy: string[];
  identifiers: {
    actor: DescriptorFieldValue;
    flow: DescriptorFieldValue;
    unit: DescriptorFieldValue;
    location: DescriptorFieldValue;
  };
  timestampField: DescriptorFieldValue;
  levelField: DescriptorFieldValue;
  messageField: DescriptorFieldValue;
  errorSignals: { fields: string[]; levelValues: string[] };
  vocabulary: {
    eventUnit: string;
    flowUnit: string;
    actorUnit: string;
    routingUnit: string;
  };
  knownPatterns: string[];
  domainDescription: string;
}

export interface ConversationSummary {
  id: string;
  projectId: string;
  title: string;
  preview: string;
  author: string;
  verdict: Verdict;
  hasTicket: boolean;
  hasCodeContext: boolean;
  createdAtIso: string;
  participants: string[];
}

export type ChatRole = "user" | "assistant" | "tool";

export interface ToolCall {
  name: string;
  server?: string;
  input: string;
  output: string;
  latencyMs: number;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  toolCall?: ToolCall;
  verdict?: Verdict;
  createdAtIso: string;
}

export interface EvidenceItem {
  id: string;
  source: string;
  timestampIso: string;
  snippet: string;
  correlationId: string;
}

export interface McpTool {
  name: string;
  description: string;
  inputSchema: string;
  callsLast24h: number;
  writeCapable: boolean;
  whitelisted: boolean;
}

export interface McpResource {
  uriTemplate: string;
  description: string;
  lastReadIso: string | null;
}

export interface McpInvocation {
  id: string;
  toolName: string;
  inputPreview: string;
  outputPreview: string;
  latencyMs: number;
  atIso: string;
  success: boolean;
}

export interface McpServer {
  id: string;
  projectId: string;
  name: string;
  transport: McpTransport;
  endpoint: string;
  status: McpStatus;
  lastHeartbeatIso: string;
  tools: McpTool[];
  resources: McpResource[];
  invocations: McpInvocation[];
}

export interface JiraTicket {
  id: string;
  projectId: string;
  key: string;
  title: string;
  verdict: Verdict;
  createdAtIso: string;
  status: "open" | "in_progress" | "done";
  assignee: string;
  url: string;
}

export interface JiraConfig {
  projectId: string;
  connected: boolean;
  site: string;
  jiraProjectKey: string;
  defaultIssueType: string;
  defaultPriority: string;
  managerTriggeredOnly: true;
}

export interface Member {
  id: string;
  name: string;
  email: string;
  role: "admin" | "owner" | "member" | "viewer";
  joinedAtIso: string;
}

// ── SSE streaming types (matches backend app/api/routes/chat.py) ──────────

export type AgentNodeName =
  | "classify_question"
  | "rewrite_question"
  | "resolve_context"
  | "retrieve_docs"
  | "rerank_docs"
  | "generate_answer"
  | "classify_issue";

export type NodeStatus = "running" | "done";

export interface SourceDocumentDTO {
  content: string;
  chunk_type: string;
  customer_id: string;
  execution_id: string;
  journey_id: string;
  page_path: string;
  action: string;
  step_order: number | null;
  target: string;
  decision_result: string | number | boolean | null;
  status: string;
  error_code: string;
}

export interface SSESessionEvent {
  type: "session";
  session_id: string;
}

export interface SSEStatusEvent {
  type: "status";
  node: AgentNodeName;
}

export interface SSERetrievalEvent {
  type: "retrieval";
  retrieved_count: number;
}

export interface SSERerankEvent {
  type: "rerank";
  reranked_count: number;
}

export interface SSETokenEvent {
  type: "token";
  content: string;
}

export interface SSESourcesEvent {
  type: "sources";
  session_id: string;
  query_type: string | null;
  effective_question: string | null;
  retrieved_count: number;
  reranked_count: number;
  sources: SourceDocumentDTO[];
  issue_type: Verdict | null;
  issue_confidence: number | null;
  issue_classification_reason: string | null;
}

export interface SSEDoneEvent {
  type: "done";
}

export type SSEEvent =
  | SSESessionEvent
  | SSEStatusEvent
  | SSERetrievalEvent
  | SSERerankEvent
  | SSETokenEvent
  | SSESourcesEvent
  | SSEDoneEvent;

// ── Backend conversation/message types (from app/models/conversation_schemas.py) ─────────────

export interface BackendConversation {
  id: string;
  session_id: string;
  title: string | null;
  meta: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface BackendMessage {
  id: string;
  conversation_id: string;
  role: "human" | "ai";
  content: string;
  sources: Record<string, unknown> | null;
  agent_metadata: Record<string, unknown> | null;
  attachments: Record<string, unknown> | null;
  created_at: string;
}

export interface BackendConversationWithMessages extends BackendConversation {
  messages: BackendMessage[];
}
