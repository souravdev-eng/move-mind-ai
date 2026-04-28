"""Upload the local golden dataset to LangSmith as `golden-v1` (idempotent).

Run:  uv run python scripts/upload_dataset.py
Env:  LANGCHAIN_API_KEY must be set. LANGCHAIN_PROJECT is optional.

Each golden example becomes one LangSmith example with:
  - inputs.question
  - outputs.expected_keywords / expected_not_contains / notes / category / id
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "eval" / "golden_dataset.json"
DATASET_NAME = "golden-v1"
DATASET_DESCRIPTION = (
    "Move Mind AI — 27-question manager-facing CMS3 log triage golden dataset. "
    "Source of truth: data/eval/golden_dataset.json."
)


def main() -> int:
    if not (os.environ.get("LANGCHAIN_API_KEY") or settings.LANGCHAIN_API_KEY):
        print("LANGCHAIN_API_KEY is not set; aborting.", file=sys.stderr)
        return 1

    from langsmith import Client

    client = Client()

    examples = json.loads(DATASET_PATH.read_text())
    print(f"Loaded {len(examples)} examples from {DATASET_PATH}")

    existing = next(
        (ds for ds in client.list_datasets(dataset_name=DATASET_NAME)), None
    )
    if existing is None:
        dataset = client.create_dataset(
            dataset_name=DATASET_NAME,
            description=DATASET_DESCRIPTION,
        )
        print(f"Created dataset {DATASET_NAME} ({dataset.id})")
    else:
        dataset = existing
        print(f"Reusing existing dataset {DATASET_NAME} ({dataset.id})")

    existing_by_id = {
        ex.outputs.get("id"): ex
        for ex in client.list_examples(dataset_id=dataset.id)
        if ex.outputs
    }

    to_create = [ex for ex in examples if ex["id"] not in existing_by_id]
    to_update = [
        (existing_by_id[ex["id"]], ex)
        for ex in examples
        if ex["id"] in existing_by_id
        and not existing_by_id[ex["id"]].outputs.get("answer")
    ]

    if to_create:
        inputs = [{"question": ex["question"]} for ex in to_create]
        outputs = [
            {
                "id": ex["id"],
                "category": ex["category"],
                "expected_keywords": ex.get("expected_keywords", []),
                "expected_not_contains": ex.get("expected_not_contains", []),
                "notes": ex.get("notes", ""),
                "prior_question": ex.get("prior_question"),
                "answer": ex.get("ground_truth", ""),
            }
            for ex in to_create
        ]
        client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)
        print(f"Created {len(to_create)} new examples in {DATASET_NAME}.")
    else:
        print("No new examples to create.")

    if to_update:
        for langsmith_ex, local_ex in to_update:
            client.update_example(
                example_id=langsmith_ex.id,
                outputs={
                    **langsmith_ex.outputs,
                    "answer": local_ex.get("ground_truth", ""),
                },
            )
        print(f"Updated {len(to_update)} existing examples with ground_truth answer.")
    else:
        print("All existing examples already have an answer — nothing to update.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
