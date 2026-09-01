import json

from llm_theory_lab.registry import run_toy_suite
from llm_theory_lab.result import write_report


def test_report_writes_json_and_markdown(tmp_path) -> None:
    result = run_toy_suite(["C02"])
    json_path = tmp_path / "result.json"
    markdown_path = tmp_path / "report.md"
    write_report(result, json_path=json_path, markdown_path=markdown_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload[0]["experiment_id"] == "C02"
    assert payload[0]["status"] == "pass"
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "C02" in markdown
    assert "温度、softmax 与 token 赔率" in markdown
