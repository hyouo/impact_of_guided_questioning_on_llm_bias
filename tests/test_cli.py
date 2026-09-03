import json
from pathlib import Path

from llm_theory_lab.cli import main


def test_cli_list(capsys) -> None:
    main(["list"])
    output = capsys.readouterr().out
    assert "C01" in output
    assert "C09" in output


def test_cli_course_human(capsys) -> None:
    main(["course"])
    output = capsys.readouterr().out
    assert "M01" in output
    assert "M08" in output
    assert "综合项目" in output


def test_cli_course_json(capsys) -> None:
    main(["course", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["id"] == "M01"
    assert payload[-1]["id"] == "M08"


def test_cli_explain(capsys) -> None:
    main(["explain", "c04"])
    output = capsys.readouterr().out
    assert "QK" in output
    assert "禁止外推" in output
    assert "c04-attention-routing.md" in output


def test_cli_explain_json(capsys) -> None:
    main(["explain", "C07", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["experiment_id"] == "C07"
    assert "probe" in payload["why_it_matters"].lower()


def test_cli_run_selected_toy(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports"
    main(["run-toy", "--ids", "C01", "C02", "--output-dir", str(output_dir)])
    assert (output_dir / "results.json").exists()
    assert (output_dir / "report.md").exists()
