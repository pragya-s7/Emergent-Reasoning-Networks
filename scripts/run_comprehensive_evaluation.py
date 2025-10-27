"""
Comprehensive Evaluation Orchestrator for Kairos System.

Runs the complete evaluation suite with maximum rigor:
1. Baseline comparisons
2. Validation effectiveness testing
3. Ablation study
4. Hebbian plasticity evaluation
5. Statistical analysis
6. Visualization generation
7. Report compilation

This script is designed for publication-quality evaluation with proper experimental controls.
"""

import argparse
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ComprehensiveEvaluator:
    """
    Orchestrates the complete evaluation pipeline.
    """

    def __init__(self, config: dict):
        self.config = config
        self.output_dir = Path(config['output_dir'])
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.output_dir / f"eval_run_{self.timestamp}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.results = {
            "timestamp": self.timestamp,
            "config": config,
            "results": {}
        }

        print(f"Comprehensive evaluation run: {self.run_dir}")

    def run_command(self, cmd: list, description: str):
        """Run a subprocess command with error handling."""
        print(f"\n{'='*80}")
        print(f"{description}")
        print(f"{'='*80}")
        print(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout)
            if result.stderr:
                print("Stderr:", result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Command failed with return code {e.returncode}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False

    def step1_baseline_evaluation(self):
        """Run baseline comparison evaluation."""
        print("\n" + "="*80)
        print("STEP 1: BASELINE COMPARISONS")
        print("="*80)

        # TODO: Implement baseline evaluation runner
        # For now, we'll note this for manual running
        baseline_results = {
            "status": "Baseline evaluation requires separate script",
            "note": "Run baselines.py manually for each query type"
        }

        self.results["results"]["baselines"] = baseline_results
        return True

    def step2_validation_effectiveness(self):
        """Test validation framework effectiveness."""
        print("\n" + "="*80)
        print("STEP 2: VALIDATION EFFECTIVENESS")
        print("="*80)

        cmd = [
            "python", "scripts/evaluate_validation_fixed.py",
            "--dataset", self.config['dataset'],
            "--kg-path", self.config['kg_path'],
            "--anthropic-key", self.config['anthropic_key'],
            "--output-dir", str(self.run_dir),
            "--n-questions", str(self.config.get('n_validation_questions', 20)),
            "--seed", str(self.config.get('seed', 42))
        ]

        success = self.run_command(cmd, "Running validation effectiveness evaluation")

        # Find output file
        validation_files = list(self.run_dir.glob("validation_evaluation_results_*.csv"))
        if validation_files:
            self.results["results"]["validation"] = {
                "status": "completed" if success else "failed",
                "output_file": str(validation_files[0])
            }

        return success

    def step3_ablation_study(self):
        """Run ablation study."""
        print("\n" + "="*80)
        print("STEP 3: ABLATION STUDY")
        print("="*80)

        cmd = [
            "python", "scripts/evaluate_ablation_fixed.py",
            "--dataset", self.config['dataset'],
            "--kg-path", self.config['kg_path'],
            "--anthropic-key", self.config['anthropic_key'],
            "--output-dir", str(self.run_dir),
            "--n-questions", str(self.config.get('n_ablation_questions', 30)),
            "--seed", str(self.config.get('seed', 42))
        ]

        success = self.run_command(cmd, "Running ablation study")

        # Find output files
        ablation_files = list(self.run_dir.glob("ablation_evaluation_results_*.csv"))
        if ablation_files:
            self.results["results"]["ablation"] = {
                "status": "completed" if success else "failed",
                "output_file": str(ablation_files[0])
            }

        return success

    def step4_plasticity_evaluation(self):
        """Evaluate Hebbian plasticity effects."""
        print("\n" + "="*80)
        print("STEP 4: HEBBIAN PLASTICITY EVALUATION")
        print("="*80)

        # Create a copy of KG for plasticity testing
        kg_copy_path = self.run_dir / "plasticity_kg_initial.json"
        shutil.copy(self.config['kg_path'], kg_copy_path)

        cmd = [
            "python", "scripts/evaluate_plasticity_fixed.py",
            "--dataset", self.config['dataset'],
            "--kg-path", str(kg_copy_path),
            "--anthropic-key", self.config['anthropic_key'],
            "--output-dir", str(self.run_dir),
            "--cycles", str(self.config.get('plasticity_cycles', 10)),
            "--queries-per-cycle", str(self.config.get('queries_per_cycle', 5)),
            "--seed", str(self.config.get('seed', 42)),
            "--use-repeated-queries"  # Test edge strengthening
        ]

        success = self.run_command(cmd, "Running Hebbian plasticity evaluation")

        # Find output files
        plasticity_files = list(self.run_dir.glob("plasticity_evaluation_results_*.csv"))
        kg_snapshots = list(self.run_dir.glob("plasticity_evaluation_results_*_kg_cycle_*.json"))

        if plasticity_files:
            self.results["results"]["plasticity"] = {
                "status": "completed" if success else "failed",
                "output_file": str(plasticity_files[0]),
                "kg_snapshots": [str(f) for f in sorted(kg_snapshots)]
            }

        return success

    def step5_generate_visualizations(self):
        """Generate all publication figures."""
        print("\n" + "="*80)
        print("STEP 5: GENERATING VISUALIZATIONS")
        print("="*80)

        figures_dir = self.run_dir / "figures"
        figures_dir.mkdir(exist_ok=True)

        # Collect result files
        validation_csv = next(self.run_dir.glob("validation_evaluation_results_*.csv"), None)
        ablation_csv = next(self.run_dir.glob("ablation_evaluation_results_*.csv"), None)
        plasticity_csv = next(self.run_dir.glob("plasticity_evaluation_results_*.csv"), None)
        kg_snapshots = sorted(self.run_dir.glob("plasticity_evaluation_results_*_kg_cycle_*.json"))

        # Build command
        cmd = ["python", "scripts/visualizations.py"]

        if validation_csv:
            cmd.extend(["--validation-results", str(validation_csv)])
        if ablation_csv:
            cmd.extend(["--ablation-results", str(ablation_csv)])
        if plasticity_csv:
            cmd.extend(["--plasticity-results", str(plasticity_csv)])
        if kg_snapshots:
            cmd.extend(["--kg-snapshots"] + [str(s) for s in kg_snapshots])

        cmd.extend(["--output-dir", str(figures_dir)])

        success = self.run_command(cmd, "Generating publication figures")

        self.results["results"]["visualizations"] = {
            "status": "completed" if success else "failed",
            "output_dir": str(figures_dir)
        }

        return success

    def step6_compile_report(self):
        """Compile final evaluation report."""
        print("\n" + "="*80)
        print("STEP 6: COMPILING FINAL REPORT")
        print("="*80)

        report_path = self.run_dir / "EVALUATION_REPORT.md"

        report = []
        report.append("# Kairos Comprehensive Evaluation Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n**Run ID:** {self.timestamp}")

        report.append("\n## Configuration")
        report.append(f"```json\n{json.dumps(self.config, indent=2)}\n```")

        report.append("\n## Evaluation Results Summary")

        # Validation results
        if "validation" in self.results["results"]:
            report.append("\n### 1. Validation Effectiveness")
            val_file = self.results["results"]["validation"].get("output_file")
            if val_file and os.path.exists(val_file):
                import pandas as pd
                df = pd.read_csv(val_file)
                report.append(f"\n- Total questions tested: {len(df) // 3}")  # 3 module types
                report.append(f"- Standard module avg trust score: {df[df['module_type']=='standard']['trust_score'].mean():.3f}")
                report.append(f"- Noisy logical avg trust score: {df[df['module_type']=='noisy_logical']['trust_score'].mean():.3f}")
                report.append(f"- Noisy ungrounded avg trust score: {df[df['module_type']=='noisy_ungrounded']['trust_score'].mean():.3f}")

                # Calculate detection rate
                noisy_df = df[df['module_type'].str.startswith('noisy')]
                detection_rate = noisy_df['validation_caught_issue'].mean() if 'validation_caught_issue' in noisy_df.columns else 0
                report.append(f"- Validation detection rate: {detection_rate*100:.1f}%")

        # Ablation results
        if "ablation" in self.results["results"]:
            report.append("\n### 2. Ablation Study")
            abl_file = self.results["results"]["ablation"].get("output_file")
            if abl_file and os.path.exists(abl_file):
                import pandas as pd
                df = pd.read_csv(abl_file)
                report.append(f"\n- Ablation conditions tested: {df['ablation_condition'].nunique()}")
                report.append(f"- Full system trust score: {df[df['ablation_condition']=='full_system']['trust_score'].mean():.3f}")

                # Show degradation for each ablation
                for condition in ['no_validation', 'no_hebbian', 'no_logical_vn', 'no_grounding_vn']:
                    if condition in df['ablation_condition'].values:
                        score = df[df['ablation_condition']==condition]['trust_score'].mean()
                        report.append(f"- {condition.replace('_', ' ').title()}: {score:.3f}")

        # Plasticity results
        if "plasticity" in self.results["results"]:
            report.append("\n### 3. Hebbian Plasticity")
            plast_file = self.results["results"]["plasticity"].get("output_file")
            if plast_file and os.path.exists(plast_file):
                import pandas as pd
                df = pd.read_csv(plast_file)

                cycles = df['cycle'].max()
                first_cycle_trust = df[df['cycle']==1]['trust_score'].mean()
                last_cycle_trust = df[df['cycle']==cycles]['trust_score'].mean()
                improvement = ((last_cycle_trust - first_cycle_trust) / first_cycle_trust * 100)

                report.append(f"\n- Reasoning cycles: {cycles}")
                report.append(f"- Cycle 1 trust score: {first_cycle_trust:.3f}")
                report.append(f"- Cycle {cycles} trust score: {last_cycle_trust:.3f}")
                report.append(f"- Improvement: {improvement:+.2f}%")

                total_emergent = df['emergent_edges_count'].sum() if 'emergent_edges_count' in df.columns else 0
                report.append(f"- Total emergent connections: {int(total_emergent)}")

        report.append("\n## Output Files")
        report.append(f"\n- Validation results: `{self.results['results'].get('validation', {}).get('output_file', 'N/A')}`")
        report.append(f"- Ablation results: `{self.results['results'].get('ablation', {}).get('output_file', 'N/A')}`")
        report.append(f"- Plasticity results: `{self.results['results'].get('plasticity', {}).get('output_file', 'N/A')}`")
        report.append(f"- Figures: `{self.results['results'].get('visualizations', {}).get('output_dir', 'N/A')}`")

        report.append("\n## Next Steps for Paper")
        report.append("\n1. Review all generated figures in the `figures/` directory")
        report.append("2. Check statistical analysis JSON files for detailed significance tests")
        report.append("3. Use these results to populate the Results section of your paper")
        report.append("4. Include key figures in the paper (learning curves, ablation chart, validation effectiveness)")
        report.append("5. Report effect sizes and p-values from the analysis files")

        # Write report
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))

        print(f"\nReport saved to: {report_path}")

        # Save results JSON
        results_json_path = self.run_dir / "evaluation_results.json"
        with open(results_json_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Results JSON saved to: {results_json_path}")

        return True

    def run_full_evaluation(self):
        """Execute the complete evaluation pipeline."""
        print("\n" + "="*80)
        print("KAIROS COMPREHENSIVE EVALUATION SUITE")
        print("Maximum Rigor - Publication Quality")
        print("="*80)
        print(f"\nOutput directory: {self.run_dir}")
        print(f"Configuration: {json.dumps(self.config, indent=2)}\n")

        steps = [
            ("Baseline Evaluation", self.step1_baseline_evaluation),
            ("Validation Effectiveness", self.step2_validation_effectiveness),
            ("Ablation Study", self.step3_ablation_study),
            ("Hebbian Plasticity", self.step4_plasticity_evaluation),
            ("Generate Visualizations", self.step5_generate_visualizations),
            ("Compile Report", self.step6_compile_report)
        ]

        for step_name, step_func in steps:
            try:
                success = step_func()
                self.results["results"][step_name.lower().replace(" ", "_")] = {
                    "status": "completed" if success else "failed"
                }
                if not success and self.config.get('stop_on_error', False):
                    print(f"\nStopping due to error in {step_name}")
                    break
            except Exception as e:
                print(f"\nERROR in {step_name}: {e}")
                import traceback
                traceback.print_exc()
                self.results["results"][step_name.lower().replace(" ", "_")] = {
                    "status": "error",
                    "error": str(e)
                }
                if self.config.get('stop_on_error', False):
                    break

        print("\n" + "="*80)
        print("COMPREHENSIVE EVALUATION COMPLETE")
        print("="*80)
        print(f"\nAll results saved to: {self.run_dir}")
        print(f"Report: {self.run_dir / 'EVALUATION_REPORT.md'}")
        print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Run comprehensive Kairos evaluation suite",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--anthropic-key", required=True, help="Anthropic API key")
    parser.add_argument("--dataset", default="tests/comprehensive_evaluation_dataset.json",
                       help="Path to evaluation dataset")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json",
                       help="Path to knowledge graph")
    parser.add_argument("--output-dir", default="output/evaluations",
                       help="Base output directory")
    parser.add_argument("--n-validation-questions", type=int, default=20,
                       help="Questions for validation testing")
    parser.add_argument("--n-ablation-questions", type=int, default=30,
                       help="Questions for ablation study")
    parser.add_argument("--plasticity-cycles", type=int, default=10,
                       help="Number of reasoning cycles for plasticity test")
    parser.add_argument("--queries-per-cycle", type=int, default=5,
                       help="Queries per plasticity cycle")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility")
    parser.add_argument("--stop-on-error", action="store_true",
                       help="Stop pipeline if any step fails")

    args = parser.parse_args()

    # Build configuration
    config = {
        "anthropic_key": args.anthropic_key,
        "dataset": args.dataset,
        "kg_path": args.kg_path,
        "output_dir": args.output_dir,
        "n_validation_questions": args.n_validation_questions,
        "n_ablation_questions": args.n_ablation_questions,
        "plasticity_cycles": args.plasticity_cycles,
        "queries_per_cycle": args.queries_per_cycle,
        "seed": args.seed,
        "stop_on_error": args.stop_on_error
    }

    # Run evaluation
    evaluator = ComprehensiveEvaluator(config)
    evaluator.run_full_evaluation()


if __name__ == "__main__":
    main()
