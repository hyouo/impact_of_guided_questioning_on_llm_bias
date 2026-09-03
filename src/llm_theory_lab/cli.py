"""Command-line interface for the theory lab."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .experiments.hf_models import (
    run_activation_patch_scan,
    run_prefix_feedback,
    run_tokenization_sensitivity,
)
from .learning import get_experiment_guide, list_course_modules
from .registry import get_experiment, list_experiments, run_toy_suite
from .result import ExperimentResult, write_report


def _print_result(result: ExperimentResult) -> None:
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm-theory-lab",
        description="Learn and test theory-linked LLM mechanism claims.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="list transparent toy experiments")

    course = subparsers.add_parser("course", help="show the guided learning modules")
    course.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    explain = subparsers.add_parser(
        "explain",
        help="explain one experiment, its readings, metrics, and evidence boundary",
    )
    explain.add_argument("experiment_id", help="experiment ID, for example C04")
    explain.add_argument("--json", action="store_true", help="emit machine-readable JSON")

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


def _course_payload() -> list[dict[str, Any]]:
    return [
        {
            "id": module["id"],
            "title": module["title"],
            "prerequisites": module["prerequisites"],
            "estimated_hours": module["estimated_hours"],
            "labs": module["labs"],
            "chapter": module["chapter"],
            "outcomes": module["outcomes"],
            "deliverable": module["deliverable"],
        }
        for module in list_course_modules()
    ]


def _print_course() -> None:
    print("LLM Theory Lab guided course")
    print("读章节 → 写预测 → 跑实验 → 解释指标 → 做练习 → 限制结论\n")
    for module in _course_payload():
        prerequisites = ", ".join(module["prerequisites"]) or "无"
        labs = ", ".join(module["labs"]) or "综合项目"
        print(f"{module['id']}｜{module['title']} ({module['estimated_hours']} h)")
        print(f"  先修: {prerequisites}; 实验: {labs}")
        print(f"  章节: {module['chapter']}")
        print(f"  产出: {module['deliverable']}")


def _explanation_payload(experiment_id: str) -> dict[str, Any]:
    spec = get_experiment(experiment_id)
    guide = get_experiment_guide(experiment_id)
    return {
        "experiment_id": spec.experiment_id,
        "title": spec.title,
        "category": spec.category,
        "theory_claim": spec.theory_claim,
        "why_it_matters": guide["why_it_matters"],
        "readings": guide["readings"],
        "guide": guide["guide"],
        "inspection_points": guide["inspection_points"],
        "falsifier": spec.falsifier,
        "allowed_conclusion": guide["allowed_conclusion"],
        "forbidden_inference": guide["forbidden_inference"],
        "run_command": f"llm-theory-lab run-toy --ids {spec.experiment_id}",
    }


def _print_explanation(experiment_id: str) -> None:
    payload = _explanation_payload(experiment_id)
    print(f"{payload['experiment_id']}｜{payload['title']}")
    print(f"理论命题: {payload['theory_claim']}")
    print(f"为什么重要: {payload['why_it_matters']}")
    print("重点观察:")
    for item in payload["inspection_points"]:
        print(f"  - {item}")
    print("先读:")
    for item in payload["readings"]:
        print(f"  - {item}")
    print(f"实验手册: {payload['guide']}")
    print(f"反证条件: {payload['falsifier']}")
    print(f"最大允许结论: {payload['allowed_conclusion']}")
    print(f"禁止外推: {payload['forbidden_inference']}")
    print(f"运行: {payload['run_command']}")


def main(argv: Sequence[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        for spec in list_experiments():
            print(f"{spec.experiment_id}\t{spec.category}\t{spec.title}\n  {spec.theory_claim}")
        return

    if args.command == "course":
        if args.json:
            print(json.dumps(_course_payload(), ensure_ascii=False, indent=2))
        else:
            _print_course()
        return

    if args.command == "explain":
        try:
            payload = _explanation_payload(args.experiment_id)
        except KeyError as exc:
            parser.error(str(exc))
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            _print_explanation(args.experiment_id)
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
