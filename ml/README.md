# QueryMind ML — text-to-SQL training pipeline (DVC)

This is a **separate, standalone research pipeline** — it trains a small local text-to-SQL model
as an experiment. It is **not** wired into the running app: `/api/chat` in the production backend
always uses the OpenAI API via `backend/app/services/sql_generator.py`. Nothing here changes that
behavior; this directory exists to demonstrate/version a from-scratch trainable alternative and to
give the sales dataset real DVC-tracked version history.

## Why DVC

- **`backend/data/superstore.csv` is now DVC-tracked** (`backend/data/superstore.csv.dvc`). When the
  dataset changes (new rows, a new time range, a schema tweak), `dvc add backend/data/superstore.csv`
  records a new version, `git commit` captures *that the data changed* without bloating the git
  history with a multi-MB CSV diff, and `dvc push` shares the new blob via the configured remote.
- **The training pipeline is a DVC pipeline** (`dvc.yaml` + `params.yaml` at the repo root): three
  stages — `generate_data` → `train` → `evaluate` — each with explicit deps/outs/params, so
  `dvc repro` only re-runs what actually changed (e.g. touching a training hyperparameter re-runs
  `train` + `evaluate` but not `generate_data`; a new CSV re-runs all three).
- **`generate_data` depends on `backend/data/superstore.csv` directly** — it reads real
  region/state/category/sub-category/city values out of the current dataset to ground its
  templated questions, so a genuinely different dataset produces a genuinely different training set,
  not just a re-run of the same hardcoded examples.

## Pipeline stages

| Stage | Script | What it does |
|---|---|---|
| `generate_data` | `ml/src/generate_training_data.py` | Builds templated `(question, SQL)` pairs over the `sales` schema, grounded in real dimension values from the CSV. Writes `ml/data/{train,val,test}.jsonl`. |
| `train` | `ml/src/train.py` | Fine-tunes `google/flan-t5-small` (configurable) on the training split with HuggingFace `Seq2SeqTrainer`. Saves to `ml/models/text2sql/`. |
| `evaluate` | `ml/src/evaluate.py` | Runs the fine-tuned model on the held-out test split, computes exact-match and valid-read-only-SQL rate (via SQLGlot, mirroring the backend validator's rules), writes `ml/metrics.json`. |

Hyperparameters live in **`params.yaml`** at the repo root (`generate_data.*` and `train.*`
sections) — DVC uses this file to know when a stage needs to re-run.

## Running it

```bash
cd "Project 01"
python -m venv ml/.venv
ml/.venv/Scripts/activate        # Windows; macOS/Linux: source ml/.venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r ml/requirements.txt

dvc repro          # runs generate_data -> train -> evaluate (only what's stale)
dvc metrics show   # prints ml/metrics.json
dvc dag            # visualizes the pipeline graph
```

To pull/push data or model versions through the configured remote:

```bash
dvc push   # upload the current data/model blobs to the remote
dvc pull   # fetch them on another machine/clone
```

## The DVC remote

`.dvc/config` points at a **local folder remote** (`../dvc-storage`, a sibling of the repo) —
there are no cloud credentials wired up. For a real deployment, swap it for S3/GCS/Azure/etc.:

```bash
dvc remote add -d storage s3://your-bucket/querymind-dvc
```

## Versioning a new dataset

```bash
# replace backend/data/superstore.csv with the new data, then:
dvc add backend/data/superstore.csv
git add backend/data/superstore.csv.dvc backend/data/.gitignore
git commit -m "data: update sales dataset"
dvc repro           # regenerates training data + retrains + re-evaluates against the new data
dvc push
```

## Sample results

From an actual `dvc repro` run (336 train / 41 val / 41 test examples, 3 epochs, CPU-only):

```json
{
  "n_test": 41,
  "exact_match": 0.6585,
  "valid_sql_rate": 0.6829
}
```

i.e. ~66% of held-out questions got the exact reference SQL, and ~68% produced syntactically valid,
read-only SQL — a reasonable result for a 77M-parameter model fine-tuned on a few hundred templated
examples in minutes on a CPU. Re-run `dvc repro` after changing `params.yaml` or the dataset to get
fresh numbers; `dvc metrics show` displays the current ones without re-running anything.

## Model scope and limitations

This is a small, CPU-trainable demo model (flan-t5-small, ~77M params) trained on a few hundred
templated examples — it's meant to show a real, reproducible training loop and DVC-tracked
artifacts, not to replace the OpenAI-backed production pipeline, which has far broader language
understanding, the ambiguity/hallucination guardrails in `backend/app/prompts/sql_prompt.py`, and
full schema/security validation regardless of which generator produced the SQL. Any output from this
model would still need to pass through `backend/app/services/sql_validator.py` before ever touching
the database — the same is true here in principle, but this pipeline is not connected to a live
database at all.
