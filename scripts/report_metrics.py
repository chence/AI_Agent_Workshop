import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
metrics_path = ROOT / "artifacts" / "metrics.json"
report_path = ROOT / "artifacts" / "metrics_report.md"

metrics = json.loads(metrics_path.read_text())
report = f"""# Day 2 Evaluation Report

- Jurisdiction accuracy: {metrics['jurisdiction_accuracy']:.3f}
- Responsible body accuracy: {metrics['responsible_body_accuracy']:.3f}
- Source presence rate: {metrics['source_presence_rate']:.3f}
- Average confidence: {metrics['avg_confidence']:.3f}
- Number of examples: {metrics['n_examples']}
- Model name: {metrics['config']['model_name']}
- Tool calling enabled: {metrics['config']['use_tool_calling']}
- Retrieval top_k: {metrics['config']['top_k']}
- Retrieval min_score: {metrics['config']['min_score']}
- Ambiguity margin: {metrics['config']['ambiguity_margin']}
"""
report_path.write_text(report)
print(report)
