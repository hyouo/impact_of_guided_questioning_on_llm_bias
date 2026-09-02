"""Command-line interface for the theory lab."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .experiments.hf_models import (
    run_activation_patch_scan,
    run_prefix_feedback,
    run_tokenization_sensitivity,
)
from .registry import list_experiments, run_toy_suite
from .result import ExperimentResult, write_report


def _print_result(result: ExperimentResult) -> None:
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm-theory-lab",
        description="Run theory-linked LLM mechanism experiments.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="list transparent toy experiments")

    toy = subparsers.add_parser("run-toy", help="run the transparent toy suite")
    toy.add_argument(
        "--ids",
        nargs="*",
        default=None,
        help="optional experiment IDs, e.g. C01 C04 C07",
    )
    toy.add_argument("--output-dir", default="reports/toy", help="report directory")

    tokenization = subparsers.add_parser(
        "hf-tokenization",
        help="compare two prompts on an open Hugging Face causal LM",
    )
    tokenization.add_argument("--model", default="openai-community/gpt2")
    tokenization.add_argument("--prompt-a", default="A careful answer begins with")
    tokenization.add_argument("--prompt-b", default="A careful answer begins with\n")
    tokenization.add_argument("--device", default="cpu")
    tokenization.add_argument("--top-k", type=int, default=10)
    tokenization.add_argument("--seed", type=int, default=0)
    tokenization.add_argument("--output", default="reports/hf_tokenization.json")

    prefix = subparsers.add_parser(
        "hf-prefix",
        help="compare the next distribution after two alternative prefixes",
    )
    prefix.add_argument("--model", default="openai-community/gpt2")
    prefix.add_argument("--prompt", default="The response begins:")
    prefix.add_argument("--prefix-a", default=" Yes")
    prefix.add_argument("--prefix-b", default=" No")
    prefix.add_argument("--device", default="cpu")
    prefix.add_argument("--top-k", type=int, default=10)
    prefix.add_argument("--seed", type=int, default=0)
    prefix.add_argument("--output", default="reports/hf_prefix.json")

    patch = subparsers.add_parser(
        "hf-patch",
        help="scan GPT-2 layers with a final-position activation patch",
    )
    patch.add_argument("--model", default="openai-community/gpt2")
    patch.add_argument("--clean", default="The capital of France is")
    patch.add_argument("--corrupted", default="The capital of Italy is")
    patch.add_argument("--target-token", default=" Paris")
    patch.add_argument("--device", default="cpu")
    patch.add_argument("--seed", type=int, default=0)
    patch.add_argument("--output", default="reports/hf_patch.json")

    return parser


def _write_single(result: ExperimentResult, path: str) -> None:
    target = Path(path)
    write_report([result], json_path=target, markdown_path=target.with_suffix(".md"))
    _print_result(result)


def main(argv: Sequence[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        for spec in list_experiments():
            print(f"{spec.experiment_id}\t{spec.category}\t{spec.title}\n  {spec.theory_claim}")
        return

    if args.command == "run-toy":
        results = run_toy_suite(args.ids)
        output_dir = Path(args.output_dir)
        write_report(
            results,
            json_path=output_dir / "results.json",
            markdown_path=output_dir / "report.md",
        )
        for result in results:
            print(f"{result.experiment_id}: {result.status} — {result.title}")
        if any(result.status == "fail" for result in results):
            raise SystemExit(1)
        return

    if args.command == "hf-tokenization":
        result = run_tokenization_sensitivity(
            model_name=args.model,
            prompt_a=args.prompt_a,
            prompt_b=args.prompt_b,
            device=args.device,
            top_k=args.top_k,
            seed=args.seed,
        )
        _write_single(result, args.output)
        return

    if args.command == "hf-prefix":
        result = run_prefix_feedback(
            model_name=args.model,
            prompt=args.prompt,
            prefix_a=args.prefix_a,
            prefix_b=args.prefix_b,
            device=args.device,
            top_k=args.top_k,
            seed=args.seed,
        )
        _write_single(result, args.output)
        return

    if args.command == "hf-patch":
        result = run_activation_patch_scan(
            model_name=args.model,
            clean_prompt=args.clean,
            corrupted_prompt=args.corrupted,
            target_token=args.target_token,
            device=args.device,
            seed=args.seed,
        )
        _write_single(result, args.output)
        return

    parser.error(f"unsupported command: {args.command}")
