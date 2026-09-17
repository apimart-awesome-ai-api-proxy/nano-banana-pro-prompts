#!/usr/bin/env python3
"""Run every recipe in data/prompts.json through Nano Banana Pro (gemini-3-pro-image-preview) and report the cost.

    python examples/run_recipes.py --dry-run          # print the plan (safe for CI)
    python examples/run_recipes.py --limit 2          # generate the first two recipes
    python examples/run_recipes.py --category "Food"  # filter by category
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECIPES = json.loads((ROOT / "data/prompts.json").read_text())
BASE = os.environ.get("APIMART_BASE_URL", "https://api.apimart.ai/v1")


def generate(prompt: str, size: str, resolution: str) -> dict:
    import requests  # imported lazily so --dry-run needs no dependency

    headers = {"Authorization": f"Bearer {os.environ['APIMART_API_KEY']}", "Content-Type": "application/json"}
    body = {"model": "gemini-3-pro-image-preview", "prompt": prompt, "size": size, "resolution": resolution, "n": 1}
    created = requests.post(f"{BASE}/images/generations", headers=headers, json=body, timeout=60).json()
    task_id = created["data"]["id"]
    delay = 3
    for _ in range(60):
        task = requests.get(f"{BASE}/tasks/{task_id}", headers=headers, timeout=60).json()["data"]
        if task["status"] in ("completed", "failed"):
            return task
        time.sleep(delay)
        delay = min(delay * 2, 10)
    raise TimeoutError(task_id)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the prompt recipes in this repository")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--category", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    recipes = [r for r in RECIPES if not args.category or args.category.lower() in r["category"].lower()]
    if args.limit:
        recipes = recipes[: args.limit]

    print(f"{len(recipes)} recipe(s) | model gemini-3-pro-image-preview")
    spent = 0.0
    for recipe in recipes:
        print(f"- {recipe['slug']:32} {recipe['size']:5} {recipe['category']}")
        if args.dry_run:
            continue
        if not os.environ.get("APIMART_API_KEY"):
            sys.exit("set APIMART_API_KEY, or use --dry-run")
        task = generate(recipe["prompt"], recipe["size"], recipe.get("resolution", "1K"))
        spent += float(task.get("cost") or 0)
        pathlib.Path(args.out).mkdir(parents=True, exist_ok=True)
        print(f"  status={task['status']} cost={task.get('cost')} urls={task.get('result', {}).get('images', [{}])[0].get('url')}")
    if not args.dry_run:
        print(f"total reported cost: ${spent:.4f}")


if __name__ == "__main__":
    main()
