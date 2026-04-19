import { type Member } from "@/interfaces/domain";

export const members: Member[] = [
  {
    id: "mem_01",
    name: "Saurav Majumdar",
    email: "saurav@acme.io",
    role: "owner",
    joinedAtIso: "2026-01-14T10:00:00Z",
  },
  {
    id: "mem_02",
    name: "Priya Kapoor",
    email: "priya@acme.io",
    role: "admin",
    joinedAtIso: "2026-01-20T10:00:00Z",
  },
  {
    id: "mem_03",
    name: "Marco Rossi",
    email: "marco@acme.io",
    role: "member",
    joinedAtIso: "2026-02-04T10:00:00Z",
  },
  {
    id: "mem_04",
    name: "Anna Klein",
    email: "anna@acme.io",
    role: "viewer",
    joinedAtIso: "2026-03-01T10:00:00Z",
  },
];
