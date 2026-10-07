"""
Automated Multi-Domain Evaluation Suite for NICE Tiny LLM (Phase 5)
Evaluates trained model against the domain benchmark across SQL, DE, Snowflake, Databricks, PowerBI, and GenAI.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from inference.generate import TinyLLMInference
from evaluation.evaluate_sql import SQLEvaluator

BENCHMARK_PATH = Path(__file__).resolve().parent / "benchmark.json"
RESULTS_DIR = Path(__file__).resolve().parent / "results"

class ModelEvaluator:
    def __init__(self, checkpoint_path: str = None):
        self.bot = TinyLLMInference(checkpoint_path=checkpoint_path)
        self.sql_evaluator = SQLEvaluator()
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
            self.benchmark: List[Dict[str, Any]] = json.load(f)

    def calculate_keyword_coverage(self, response: str, expected_keywords: List[str]) -> float:
        """Calculates percentage of expected domain terms mentioned in the answer."""
        if not expected_keywords:
            return 1.0
        response_lower = response.lower()
        matched = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
        return matched / len(expected_keywords)

    def run_benchmark(self, max_new_tokens: int = 150, temperature: float = 0.0) -> Dict[str, Any]:
        print(f"\n[*] Starting NICE SQL-SLM Benchmark Evaluation ({len(self.benchmark)} questions)...")
        print("=" * 80)

        results = []
        category_stats = {}
        total_sql_tests = 0
        sql_syntax_passes = 0
        sql_execution_passes = 0
        sql_semantic_passes = 0
        total_table_precisions = []
        total_col_precisions = []
        latencies = []

        for idx, item in enumerate(self.benchmark, 1):
            q_id = item["id"]
            cat = item.get("category", "general")
            difficulty = item.get("difficulty", "medium")
            question = item["question"]
            schema = item.get("schema")
            gt_sql = item.get("ground_truth_sql")
            ordered = item.get("ordered", False)

            if cat not in category_stats:
                category_stats[cat] = {
                    "total": 0,
                    "syntax_valid": 0,
                    "executable": 0,
                    "semantic_pass": 0,
                    "exact_matches": 0
                }

            category_stats[cat]["total"] += 1

            # Run schema-conditioned structured inference
            t0 = time.time()
            gen_res = self.bot.generate_structured(
                question=question,
                schema=schema,
                max_new_tokens=max_new_tokens,
                temperature=temperature
            )
            latency = gen_res["latency_sec"]
            latencies.append(latency)
            generated_sql = gen_res["sql"]

            # Semantic & AST Evaluation
            sem_eval = None
            if gt_sql and generated_sql:
                total_sql_tests += 1
                sem_eval = self.sql_evaluator.evaluate_semantic_equivalence(
                    generated_sql=generated_sql,
                    ground_truth_sql=gt_sql,
                    ordered=ordered
                )
                if sem_eval["syntax_valid"]:
                    sql_syntax_passes += 1
                    category_stats[cat]["syntax_valid"] += 1
                if sem_eval["executable"]:
                    sql_execution_passes += 1
                    category_stats[cat]["executable"] += 1
                if sem_eval["result_equivalent"]:
                    sql_semantic_passes += 1
                    category_stats[cat]["semantic_pass"] += 1
                if sem_eval["exact_match"]:
                    category_stats[cat]["exact_matches"] += 1

                total_table_precisions.append(sem_eval.get("table_precision", 0.0))
                total_col_precisions.append(sem_eval.get("column_precision", 0.0))

            item_result = {
                "id": q_id,
                "category": cat,
                "difficulty": difficulty,
                "question": question,
                "schema": schema,
                "generated_sql": generated_sql,
                "ground_truth_sql": gt_sql,
                "latency_sec": latency,
                "eval": sem_eval
            }
            results.append(item_result)

            status_str = "[SEMANTIC PASS]" if sem_eval and sem_eval["result_equivalent"] else ("[SYNTAX OK]" if sem_eval and sem_eval["syntax_valid"] else "[FAIL]")
            print(f"[{idx:02d}/{len(self.benchmark):02d}] {q_id} ({cat}) {status_str} (Latency: {latency:.2f}s)")

        # Aggregate Metrics
        syntax_rate = (sql_syntax_passes / max(1, total_sql_tests)) * 100
        exec_rate = (sql_execution_passes / max(1, total_sql_tests)) * 100
        semantic_rate = (sql_semantic_passes / max(1, total_sql_tests)) * 100
        avg_table_prec = (sum(total_table_precisions) / max(1, len(total_table_precisions))) * 100 if total_table_precisions else 0.0
        avg_col_prec = (sum(total_col_precisions) / max(1, len(total_col_precisions))) * 100 if total_col_precisions else 0.0
        avg_latency = sum(latencies) / max(1, len(latencies))

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_config": str(self.bot.config),
            "total_benchmark_cases": len(self.benchmark),
            "metrics": {
                "sql_syntax_pass_rate_pct": round(syntax_rate, 2),
                "sql_execution_pass_rate_pct": round(exec_rate, 2),
                "sql_semantic_equivalence_pct": round(semantic_rate, 2),
                "avg_table_precision_pct": round(avg_table_prec, 2),
                "avg_column_precision_pct": round(avg_col_prec, 2),
                "total_sql_evaluated": total_sql_tests,
                "avg_latency_sec": round(avg_latency, 3),
            },
            "category_breakdown": category_stats,
            "detailed_results": results
        }

        self._save_reports(report)
        self._print_summary_table(report)
        return report

    def _save_reports(self, report: Dict[str, Any]):
        json_path = RESULTS_DIR / "evaluation_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        md_path = RESULTS_DIR / "evaluation_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# 📊 NICE SQL-SLM Benchmark Evaluation Report\n\n")
            f.write(f"**Date:** `{report['timestamp']}`  \n")
            f.write(f"**Total Benchmark Cases:** `{report['total_benchmark_cases']}`  \n\n")
            f.write("## 🚀 Key Metrics\n\n")
            f.write(f"- **Semantic Result Equivalence:** `{report['metrics']['sql_semantic_equivalence_pct']}%`\n")
            f.write(f"- **SQL Sandbox Execution Rate:** `{report['metrics']['sql_execution_pass_rate_pct']}%`\n")
            f.write(f"- **SQL Syntax Validity Rate:** `{report['metrics']['sql_syntax_pass_rate_pct']}%`\n")
            f.write(f"- **Table Precision:** `{report['metrics']['avg_table_precision_pct']}%`\n")
            f.write(f"- **Column Precision:** `{report['metrics']['avg_column_precision_pct']}%`\n")
            f.write(f"- **Average Inference Latency:** `{report['metrics']['avg_latency_sec']}s` on CPU\n\n")

            f.write("## 📈 Performance Breakdown by Category\n\n")
            f.write("| Category | Total | Syntax Pass (%) | Executable (%) | Semantic Match (%) |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            for c, s in report["category_breakdown"].items():
                tot = s["total"]
                syn_pct = round((s["syntax_valid"] / tot) * 100, 1) if tot > 0 else 0
                exe_pct = round((s["executable"] / tot) * 100, 1) if tot > 0 else 0
                sem_pct = round((s["semantic_pass"] / tot) * 100, 1) if tot > 0 else 0
                f.write(f"| **{c.replace('_', ' ').title()}** | {tot} | {syn_pct}% | {exe_pct}% | {sem_pct}% |\n")

        print(f"\n[+] Saved evaluation JSON report to: {json_path}")
        print(f"[+] Saved evaluation Markdown report to: {md_path}")

    def _print_summary_table(self, report: Dict[str, Any]):
        print("\n" + "=" * 80)
        print("                  SQL-SLM BENCHMARK EVALUATION SUMMARY")
        print("=" * 80)
        m = report["metrics"]
        print(f"Semantic Result Equivalence:  {m['sql_semantic_equivalence_pct']:.1f}%")
        print(f"SQL Sandbox Execution Rate:   {m['sql_execution_pass_rate_pct']:.1f}%")
        print(f"SQL Syntax Pass Rate:         {m['sql_syntax_pass_rate_pct']:.1f}%")
        print(f"Table Precision:              {m['avg_table_precision_pct']:.1f}%")
        print(f"Column Precision:             {m['avg_column_precision_pct']:.1f}%")
        print(f"Average CPU Latency:          {m['avg_latency_sec']:.3f} seconds")
        print("-" * 80)
        print(f"{'Category':<25} | {'Cases':<6} | {'Syntax (%)':<12} | {'Semantic Equiv (%)'}")
        print("-" * 80)
        for c, s in report["category_breakdown"].items():
            tot = s["total"]
            syn_pct = (s["syntax_valid"] / tot) * 100 if tot > 0 else 0
            sem_pct = (s["semantic_pass"] / tot) * 100 if tot > 0 else 0
            print(f"{c.replace('_', ' ').title():<25} | {tot:<6} | {syn_pct:<12.1f} | {sem_pct:.1f}%")
        print("=" * 80 + "\n")

if __name__ == "__main__":
    evaluator = ModelEvaluator()
    evaluator.run_benchmark()

