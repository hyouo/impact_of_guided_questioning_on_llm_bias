from pathlib import Path

import pytest

from llm_theory_lab.cli import main


def test_cli_list(capsys) -> None:
    main(["list"])
    output = capsys.readouterr().out
    assert "C01" in output
    assert "C09" in output


def test_cli_list_category(capsys) -> None:
    main(["list", "--category", "methods"])
    output = capsys.readouterr().out
    assert "C07" in output
    assert "C08" in output
    assert "C01" not in output


def test_cli_roadmap(capsys) -> None:
    main(["roadmap"])
    output = capsys.readouterr().out
    assert "模型是条件系统" in output
    assert "综合项目" in output
    assert "docs/course/01-model-as-conditional-system.md" in output


def test_cli_explain(capsys) -> None:
    main(["explain", "c07"])
    output = capsys.readouterr().out
    assert "可解码" in output
    assert "反证条件" in output
    assert "不能推出" in output
    assert "docs/labs/04-probe-vs-causality.md" in output


def test_cli_explain_unknown_is_parser_error() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["explain", "C99"])
    assert exc_info.value.code == 2


def test_cli_run_selected_toy(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports"
    main(["run-toy", "--ids", "C01", "C02", "--output-dir", str(output_dir)])
    assert (output_dir / "results.json").exists()
    assert (output_dir / "report.md").exists()
