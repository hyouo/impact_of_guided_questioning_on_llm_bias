"""Command-line interface for the theory-first learning and experiment lab."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from .evidence import (
    EvidenceValidationError,
    load_catalog_urls,
    validate_bundle,
    validate_ledger,
    write_reproduction_bundle,
)
from .experiments.hf_models import (
    run_activation_patch_scan,
    run_prefix_feedback,
    run_tokenization_sensitivity,
)
from .registry import ExperimentSpec, get_experiment, list_experiments, run_toy_suite
from .reproduction_map import (
    COVERAGE_STATUSES,
    MODES,
    PRIORITIES,
    ReproductionMapError,
    load_catalog_bytes,
    load_reproduction_map,
    select_sources,
    summarize_reproduction_map,
    validate_reproduction_map,
)
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
    print(f"主张 ID: {spec.claim_id}@{spec.claim_revision}")
    print(f"复现类型: {spec.reproduction_status}")
    print(f"理论命题: {spec.theory_claim}")
    print(f"直觉: {spec.intuition}")
    print(f"反证条件: {spec.falsifier}")
    print(f"课程: {spec.lesson_path}")
    print(f"实验手册: {spec.lab_path}")
    print(f"不能推出: {spec.does_not_show}")
    print("来源:")
    for url in spec.source_urls:
        print(f"  - {url}")
    print(f"运行: llm-theory-lab run-toy --ids {spec.experiment_id}")


def _print_reproduction_summary(summary: Mapping[str, object]) -> None:
    print(f"公开来源总数: {summary['total_sources']}")
    for heading, key in (
        ("覆盖状态", "coverage_status"),
        ("当前复现模式", "current_modes"),
        ("精确复现可行性", "exact_reproduction_feasibility"),
        ("优先级", "priority"),
    ):
        print(f"{heading}:")
        values = summary[key]
        if isinstance(values, Mapping):
            for name, count in values.items():
                print(f"  {name}: {count}")


def _print_reproduction_sources(sources: Sequence[Mapping[str, object]]) -> None:
    if not sources:
        print("没有匹配的公开来源。")
        return
    for source in sources:
        protocols = ", ".join(str(item) for item in source["protocol_ids"]) or "—"
        modes = ", ".join(str(item) for item in source["current_modes"]) or "—"
        print(
            f"{source['source_id']} | {source['period']} | {source['title']}\n"
            f"  覆盖: {source['coverage_status']}\n"
            f"  当前模式: {modes}\n"
            f"  协议: {protocols}\n"
            f"  精确复现可行性: {source['exact_reproduction_feasibility']}\n"
            f"  优先级/计算: {source['priority']} / {source['compute_tier']}\n"
            f"  下一步: {source['next_step']}\n"
            f"  来源: {source['url']}"
        )


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
        help="optional experiment IDs, e.g. C01 C04 C12",
    )
    toy.add_argument("--output-dir", default="reports/toy", help="report directory")

    reproduce = subparsers.add_parser(
        "reproduce",
        help="run CPU-safe experiments and write a self-verifying evidence bundle",
    )
    reproduce.add_argument("--ids", nargs="*", default=None, help="optional experiment IDs")
    reproduce.add_argument(
        "--output-dir",
        default="reports/reproduction",
        help="directory for results, ledger, matrix, and manifest",
    )
    reproduce.add_argument(
        "--allow-nonpassing",
        action="store_true",
        help="return success even when a result is fail or error; records are still preserved",
    )

    validate = subparsers.add_parser(
        "validate-evidence",
        help="validate an evidence ledger or a complete reproduction bundle",
    )
    validate.add_argument("path", help="ledger JSON path or reproduction bundle directory")
    validate.add_argument(
        "--bundle",
        action="store_true",
        help="treat path as a reproduction bundle directory",
    )
    validate.add_argument(
        "--allow-partial",
        action="store_true",
        help="allow a ledger or bundle that does not contain every registered experiment",
    )
    validate.add_argument(
        "--catalog",
        default="sources/transformer_circuits_catalog.csv",
        help="source catalog used to reject uncatalogued citations",
    )

    reproduction_map = subparsers.add_parser(
        "reproduction-map",
        help="inspect coverage of all public Transformer Circuits sources",
    )
    reproduction_map.add_argument(
        "--status",
        choices=sorted(COVERAGE_STATUSES),
        default=None,
        help="filter by coverage status",
    )
    reproduction_map.add_argument(
        "--mode",
        choices=sorted(MODES),
        default=None,
        help="filter by current reproduction mode",
    )
    reproduction_map.add_argument("--theme", default=None, help="filter by source theme")
    reproduction_map.add_argument(
        "--priority",
        choices=sorted(PRIORITIES),
        default=None,
        help="filter by implementation priority",
    )
    reproduction_map.add_argument(
        "--summary-only",
        action="store_true",
        help="print only aggregate coverage counts",
    )
    reproduction_map.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="emit machine-readable JSON",
    )

    subparsers.add_parser(
        "validate-reproduction-map",
        help="validate 56-source coverage, hashes, protocol mappings, and package data",
    )

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


def _load_validated_reproduction_map() -> tuple[dict[str, object], bytes]:
    registry = load_reproduction_map()
    catalog = load_catalog_bytes()
    validate_reproduction_map(registry, catalog_content=catalog)
    return registry, catalog


def main(argv: Sequence[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        specs = list_experiments()
        if args.category:
            specs = tuple(spec for spec in specs if spec.category == args.category)
        for spec in specs:
            print(f"{spec.experiment_id}\t{spec.claim_id}\t{spec.category}\t{spec.title}")
        if not specs:
            parser.error(f"no experiments found for category {args.category!r}")
        return

    if args.command == "roadmap":
        print("推荐学习路径")
        for number, title, path in COURSE_STEPS:
            print(f"{number}. {title}\n   {path}")
        print("\n开始: llm-theory-lab explain C01")
        print("完整透明复现: llm-theory-lab reproduce")
        print("公开来源覆盖: llm-theory-lab reproduction-map --summary-only")
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

    if args.command == "reproduce":
        try:
            manifest = write_reproduction_bundle(
                args.output_dir,
                experiment_ids=args.ids,
            )
        except (EvidenceValidationError, KeyError, OSError, ValueError) as exc:
            parser.error(str(exc))
        for status, count in manifest["status_counts"].items():
            print(f"{status}: {count}")
        print(f"复现清单: {Path(args.output_dir) / 'manifest.json'}")
        nonpassing = {"fail", "error", "inconclusive", "skipped"}
        if not args.allow_nonpassing and nonpassing & set(manifest["status_counts"]):
            raise SystemExit(1)
        return

    if args.command == "validate-evidence":
        require_complete = not args.allow_partial
        path = Path(args.path)
        try:
            if args.bundle:
                manifest = validate_bundle(path, require_complete=require_complete)
                print(
                    f"bundle valid: {len(manifest['experiment_ids'])} experiments, "
                    f"revision {manifest['code_revision']}"
                )
                return

            ledger = json.loads(path.read_text(encoding="utf-8"))
            catalog_path = Path(args.catalog)
            catalog_urls = load_catalog_urls(catalog_path) if catalog_path.is_file() else None
            validate_ledger(
                ledger,
                require_complete=require_complete,
                catalog_urls=catalog_urls,
            )
        except (EvidenceValidationError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(f"ledger valid: {len(ledger['records'])} records")
        return

    if args.command == "reproduction-map":
        try:
            registry, _ = _load_validated_reproduction_map()
            summary = summarize_reproduction_map(registry)
            selected = select_sources(
                registry,
                coverage_status=args.status,
                mode=args.mode,
                theme=args.theme,
                priority=args.priority,
            )
        except (OSError, ReproductionMapError, ValueError) as exc:
            parser.error(str(exc))
        if args.as_json:
            payload: dict[str, object] = {"summary": summary}
            if not args.summary_only:
                payload["sources"] = selected
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return
        _print_reproduction_summary(summary)
        if not args.summary_only:
            print(f"匹配来源: {len(selected)}")
            _print_reproduction_sources(selected)
        return

    if args.command == "validate-reproduction-map":
        try:
            registry, _ = _load_validated_reproduction_map()
            summary = summarize_reproduction_map(registry)
        except (OSError, ReproductionMapError, ValueError) as exc:
            parser.error(str(exc))
        print(
            "reproduction map valid: "
            f"{summary['total_sources']} sources; {summary['coverage_status']}"
        )
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
