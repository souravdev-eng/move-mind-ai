import { type Descriptor } from "@/interfaces/domain";

export const cms3Descriptor: Descriptor = {
  domainId: "cms3",
  displayName: "CMS3 Journey Engine",
  version: "v3",
  correlationKeys: {
    primary: {
      value: "execution_id",
      confidence: "high",
      source: "Present in 198/200 sample events",
      editedByUser: false,
    },
    secondary: {
      value: "customer_id",
      confidence: "high",
      source: "Present in 195/200 sample events",
      editedByUser: false,
    },
  },
  groupBy: ["customer_id", "execution_id"],
  identifiers: {
    actor: {
      value: "customer_id",
      confidence: "high",
      source: "Matches actor pattern in 97% of events",
      editedByUser: false,
    },
    flow: {
      value: "journey_id",
      confidence: "high",
      source: "Unique per run; 100% coverage",
      editedByUser: false,
    },
    unit: {
      value: "step_order",
      confidence: "medium",
      source: "Integer sequence; 180/200 events",
      editedByUser: true,
    },
    location: {
      value: "page_path",
      confidence: "medium",
      source: "URL-like field; 155/200 events",
      editedByUser: false,
    },
  },
  timestampField: {
    value: "timestamp",
    confidence: "high",
    source: "ISO8601 in 200/200 events",
    editedByUser: false,
  },
  levelField: {
    value: "level",
    confidence: "high",
    source: "Enum values detected",
    editedByUser: false,
  },
  messageField: {
    value: "message",
    confidence: "high",
    source: "Free-text in 200/200 events",
    editedByUser: false,
  },
  errorSignals: {
    fields: ["error_code", "error_message"],
    levelValues: ["error", "critical"],
  },
  vocabulary: {
    eventUnit: "step",
    flowUnit: "journey",
    actorUnit: "customer",
    routingUnit: "route",
  },
  knownPatterns: [
    "GraphQL has two representations: transport-level graphql_request events and named gql_* operations. These are NOT duplicates.",
    "route_entered events define the navigation path of a journey.",
  ],
  domainDescription:
    "CMS3 is a CMS agent journey orchestration engine. It routes agents through multi-step journeys, evaluates UI conditions at each step, and fires GraphQL API calls.",
};
