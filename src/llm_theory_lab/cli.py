"""Command-line interface for the theory-first learning and experiment lab."""

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
from .registry import ExperimentSpec, get_experiment, list_experiments, run_toy_suite
from .result import ExperimentResult, write_report

COURSE_STEPS: tuple[tuple[str, str, str], ...] = (
    ("1", "模型是条件系统", "docs/course/01-model-as-conditional-system.md"),
    ("2", "权重、激活与 logits", "docs/course/02-weights-activations-and-logits.md"),
    ("3", "Attention 与回路", "docs/course/03-attention-and-circuits.md"),
    ("4", "特征与 superposition", "docs/course/04-features-and-superposition.md"),
    ("5", "推理与生成反馈", "docs/course/05-reasoning-and-feedback.md"),
    ("6", "因果可解释性", "docs/course/06-causal-interpretability.md"),
    ("7", "安全路由", "docs/course/07-safety-routing.md"),
    ("8", "综合项目", "docs/course/08-capstone.md"),
)


def _print_result(result: ExperimentResult) -> None:
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def _print_spec(spec: ExperimentSpec) -> None:
    print(f"{spec.experiment_id} | {spec.title}")
    print(f"理论命题: {spec.theory_claim}")
    print(f"直觉: {spec.intuition}")
    print(f"反证条件: {spec.falsifier}")
    print(f"课程: {spec.lesson_path}")
    print(f"实验手册: {spec.lab_path}")
    print(f"不能推出: {spec.does_not_show}")
    print(f"运行: llm-theory-lab run-toy --ids {spec.experiment_id}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm-theory-lab",
        description="Learn and test theory-linked LLM mechanism claims.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    listing = subparsers.add_parser("list", help="list transparent experiments")
    listing.add_argument("--category", default=None, help="optional category filter")

    subparsers.add_parser("roadmap", help="print the recommended learning path")

    explain = subparsers.add_parser("explain", help="explain one experiment before running it")
    explain.add_argument("experiment_id", help="experiment ID, e.g. C01")

    toy = subparsers.add_parser("run-toy", help="run transparent C01-C12 experiments")
    toy.add_argument(
        "--ids",
        nargs="*",
        default=None,
        help="optional experiment IDs, e.g. C01 C04 C11",
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
        specs = list_experiments()
        if args.category:
            specs = tuple(spec for spec in specs if spec.category == args.category)
        for spec in specs:
            print(f"{spec.experiment_id}\t{spec.category}\t{spec.title}")
        if not specs:
            parser.error(f"no experiments found for category {args.category!r}")
        return

    if args.command == "roadmap":
        print("推荐学习路径")
        for number, title, path in COURSE_STEPS:
            print(f"{number}. {title}\n   {path}")
        print("\n开始: llm-theory-lab explain C01")
        return

    if args.command == "explain":
        try:
            _print_spec(get_experiment(args.experiment_id))
        except KeyError as exc:
            parser.error(str(exc))
        return

    if args.command == "run-toy":
        try:
            results = run_toy_suite(args.ids)
        except KeyError as exc:
            parser.error(str(exc))
        output_dir = Path(args.output_dir)
        write_report(
            results,
            json_path=output_dir / "results.json",
            markdown_path=output_dir / "report.md",
        )
        for result in results:
            print(f"{result.experiment_id}: {result.status} — {result.title}")
        print(f"报告: {output_dir / 'report.md'}")
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
