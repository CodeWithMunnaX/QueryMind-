"""Fine-tunes a small seq2seq model (default: flan-t5-small) to translate natural-language
questions about the `sales` table into SQL, using the templated dataset from
generate_training_data.py. This is a standalone research/prototyping pipeline — it is NOT wired
into the production /api/chat path, which uses the OpenAI API via app/services/sql_generator.py.

Usage: python ml/src/train.py (reads hyperparameters from params.yaml's `train` section).
"""
import json
from pathlib import Path

import numpy as np
import torch
import yaml
from datasets import Dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "ml" / "data"
MODEL_OUT_DIR = REPO_ROOT / "ml" / "models" / "text2sql"
PARAMS_PATH = REPO_ROOT / "params.yaml"


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    params = yaml.safe_load(PARAMS_PATH.read_text())["train"]
    torch.manual_seed(params["seed"])

    tokenizer = AutoTokenizer.from_pretrained(params["base_model"])
    model = AutoModelForSeq2SeqLM.from_pretrained(params["base_model"])

    train_records = load_jsonl(DATA_DIR / "train.jsonl")
    val_records = load_jsonl(DATA_DIR / "val.jsonl")

    def to_dataset(records: list[dict]) -> Dataset:
        return Dataset.from_dict(
            {"input": [r["input"] for r in records], "sql": [r["sql"] for r in records]}
        )

    train_ds, val_ds = to_dataset(train_records), to_dataset(val_records)

    def tokenize(batch: dict) -> dict:
        model_inputs = tokenizer(
            batch["input"], max_length=params["max_input_length"], truncation=True, padding=False
        )
        labels = tokenizer(
            text_target=batch["sql"], max_length=params["max_target_length"], truncation=True, padding=False
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    train_ds = train_ds.map(tokenize, batched=True, remove_columns=["input", "sql"])
    val_ds = val_ds.map(tokenize, batched=True, remove_columns=["input", "sql"])

    collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    def compute_metrics(eval_pred) -> dict:
        predictions, labels = eval_pred
        if isinstance(predictions, tuple):
            predictions = predictions[0]
        predictions = np.where(predictions != -100, predictions, tokenizer.pad_token_id)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        exact = sum(p.strip() == t.strip() for p, t in zip(decoded_preds, decoded_labels)) / len(decoded_labels)
        return {"exact_match": exact}

    args = Seq2SeqTrainingArguments(
        output_dir=str(REPO_ROOT / "ml" / "_trainer_tmp"),
        num_train_epochs=params["epochs"],
        per_device_train_batch_size=params["batch_size"],
        per_device_eval_batch_size=params["batch_size"],
        learning_rate=params["learning_rate"],
        eval_strategy="epoch",
        save_strategy="no",
        predict_with_generate=True,
        generation_max_length=params["max_target_length"],
        logging_steps=10,
        report_to=[],
        use_cpu=True,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    final_eval = trainer.evaluate()
    print(f"Final validation metrics: {final_eval}")

    MODEL_OUT_DIR.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(MODEL_OUT_DIR))
    tokenizer.save_pretrained(str(MODEL_OUT_DIR))
    print(f"Model saved to {MODEL_OUT_DIR}")


if __name__ == "__main__":
    main()
