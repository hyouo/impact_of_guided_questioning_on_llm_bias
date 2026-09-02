from pathlib import Path

from llm_theory_lab.cli import main


def test_cli_list(capsys) -> None:
    main(["list"])
    output = capsys.readouterr().out
    assert "C01" in output
    assert "C09" in output


def test_cli_run_selected_toy(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports"
    main(["run-toy", "--ids", "C01", "C02", "--output-dir", str(output_dir)])
    assert (output_dir / "results.json").exists()
    assert (output_dir / "report.md").exists()
