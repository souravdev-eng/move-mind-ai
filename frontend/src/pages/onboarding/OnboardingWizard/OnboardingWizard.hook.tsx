import { useState } from "react";

import { useNavigate, useParams } from "react-router-dom";

const STEPS = [
  "Project basics",
  "Connect log source",
  "Configure connector",
  "Pull sample",
  "Profiler review",
  "Confirm & ingest",
  "Ready",
] as const;

export function useOnboardingWizard() {
  const { orgSlug = "acme" } = useParams();
  const nav = useNavigate();
  const [active, setActive] = useState(0);
  const [form, setForm] = useState({
    name: "",
    slug: "",
    description: "",
    connector: "s3",
    bucket: "",
    region: "us-east-1",
  });

  const next = () => {
    setActive((a) => Math.min(a + 1, STEPS.length - 1));
  };
  const back = () => {
    setActive((a) => Math.max(a - 1, 0));
  };

  return { orgSlug, nav, active, form, setForm, next, back, steps: STEPS };
}
