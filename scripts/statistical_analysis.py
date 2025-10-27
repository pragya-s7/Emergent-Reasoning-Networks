"""
Statistical analysis utilities for evaluation results.

Provides functions for:
- Significance testing (t-tests, Wilcoxon)
- Effect size calculation (Cohen's d, r)
- Confidence intervals
- Bootstrap resampling
- Multiple comparison correction
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Any
import json


def cohens_d(group1: List[float], group2: List[float]) -> float:
    """
    Calculate Cohen's d effect size.

    Interpretation:
    - Small effect: d = 0.2
    - Medium effect: d = 0.5
    - Large effect: d = 0.8
    """
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0

    return (np.mean(group1) - np.mean(group2)) / pooled_std


def paired_ttest(group1: List[float], group2: List[float]) -> Dict[str, float]:
    """
    Perform paired t-test and return statistics.

    Returns:
        Dict with t-statistic, p-value, effect size, and CI
    """
    if len(group1) != len(group2):
        raise ValueError("Paired t-test requires equal sample sizes")

    if len(group1) < 2:
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "cohens_d": 0.0,
            "ci_lower": 0.0,
            "ci_upper": 0.0,
            "significant": False
        }

    t_stat, p_value = stats.ttest_rel(group1, group2)

    # Calculate effect size
    effect_size = cohens_d(group1, group2)

    # Calculate 95% CI for mean difference
    diff = np.array(group1) - np.array(group2)
    ci = stats.t.interval(0.95, len(diff) - 1, loc=np.mean(diff), scale=stats.sem(diff))

    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "cohens_d": float(effect_size),
        "ci_lower": float(ci[0]),
        "ci_upper": float(ci[1]),
        "significant": p_value < 0.05,
        "interpretation": interpret_effect_size(effect_size)
    }


def wilcoxon_test(group1: List[float], group2: List[float]) -> Dict[str, float]:
    """
    Perform Wilcoxon signed-rank test (non-parametric alternative to paired t-test).

    Use when data is not normally distributed.
    """
    if len(group1) != len(group2):
        raise ValueError("Wilcoxon test requires equal sample sizes")

    if len(group1) < 2:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "significant": False
        }

    statistic, p_value = stats.wilcoxon(group1, group2)

    # Calculate rank-biserial correlation (effect size for Wilcoxon)
    n = len(group1)
    r = 1 - (2 * statistic) / (n * (n + 1))

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "effect_size_r": float(r),
        "significant": p_value < 0.05
    }


def independent_ttest(group1: List[float], group2: List[float]) -> Dict[str, float]:
    """
    Perform independent t-test for unpaired samples.
    """
    if len(group1) < 2 or len(group2) < 2:
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "cohens_d": 0.0,
            "significant": False
        }

    t_stat, p_value = stats.ttest_ind(group1, group2)
    effect_size = cohens_d(group1, group2)

    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "cohens_d": float(effect_size),
        "significant": p_value < 0.05,
        "interpretation": interpret_effect_size(effect_size)
    }


def interpret_effect_size(d: float) -> str:
    """Interpret Cohen's d effect size."""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"


def bootstrap_ci(data: List[float], n_bootstrap: int = 10000, ci: float = 0.95) -> Tuple[float, float]:
    """
    Calculate bootstrap confidence interval.

    Args:
        data: Sample data
        n_bootstrap: Number of bootstrap samples
        ci: Confidence level (default 0.95)

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if len(data) < 2:
        return (0.0, 0.0)

    bootstrap_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(sample))

    alpha = 1 - ci
    lower = np.percentile(bootstrap_means, alpha / 2 * 100)
    upper = np.percentile(bootstrap_means, (1 - alpha / 2) * 100)

    return (float(lower), float(upper))


def bonferroni_correction(p_values: List[float]) -> List[float]:
    """
    Apply Bonferroni correction for multiple comparisons.

    Args:
        p_values: List of p-values from multiple tests

    Returns:
        List of corrected p-values
    """
    n_tests = len(p_values)
    return [min(p * n_tests, 1.0) for p in p_values]


def holm_bonferroni_correction(p_values: List[float]) -> List[float]:
    """
    Apply Holm-Bonferroni correction (less conservative than Bonferroni).

    Args:
        p_values: List of p-values from multiple tests

    Returns:
        List of corrected p-values
    """
    n = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]

    corrected = np.zeros(n)
    for i, p in enumerate(sorted_p):
        corrected[sorted_indices[i]] = min(p * (n - i), 1.0)

    # Enforce monotonicity
    for i in range(1, n):
        if corrected[sorted_indices[i]] < corrected[sorted_indices[i - 1]]:
            corrected[sorted_indices[i]] = corrected[sorted_indices[i - 1]]

    return corrected.tolist()


def analyze_experimental_results(results_df: pd.DataFrame, condition_col: str, metric_col: str,
                                 baseline_condition: str) -> Dict[str, Any]:
    """
    Comprehensive statistical analysis comparing experimental conditions to baseline.

    Args:
        results_df: DataFrame with results
        condition_col: Column name for experimental conditions
        metric_col: Column name for the metric to analyze
        baseline_condition: Name of the baseline condition

    Returns:
        Dict with statistical analysis results
    """
    conditions = results_df[condition_col].unique()
    baseline_data = results_df[results_df[condition_col] == baseline_condition][metric_col].tolist()

    analysis = {
        "baseline": baseline_condition,
        "metric": metric_col,
        "n_samples": len(baseline_data),
        "baseline_mean": float(np.mean(baseline_data)),
        "baseline_std": float(np.std(baseline_data, ddof=1)),
        "baseline_ci": bootstrap_ci(baseline_data),
        "comparisons": {}
    }

    p_values = []

    for condition in conditions:
        if condition == baseline_condition:
            continue

        condition_data = results_df[results_df[condition_col] == condition][metric_col].tolist()

        # Check if paired (same length and aligned)
        is_paired = len(condition_data) == len(baseline_data)

        if is_paired:
            # Paired tests
            ttest_result = paired_ttest(baseline_data, condition_data)
            wilcoxon_result = wilcoxon_test(baseline_data, condition_data)
        else:
            # Independent tests
            ttest_result = independent_ttest(baseline_data, condition_data)
            wilcoxon_result = {"note": "Unpaired data - Wilcoxon not applicable"}

        analysis["comparisons"][condition] = {
            "mean": float(np.mean(condition_data)),
            "std": float(np.std(condition_data, ddof=1)),
            "ci": bootstrap_ci(condition_data),
            "n_samples": len(condition_data),
            "improvement_pct": float((np.mean(condition_data) - np.mean(baseline_data)) / np.mean(baseline_data) * 100),
            "ttest": ttest_result,
            "wilcoxon": wilcoxon_result
        }

        if "p_value" in ttest_result:
            p_values.append(ttest_result["p_value"])

    # Apply multiple comparison correction
    if p_values:
        corrected_p = holm_bonferroni_correction(p_values)
        i = 0
        for condition in analysis["comparisons"]:
            analysis["comparisons"][condition]["ttest"]["p_value_corrected"] = corrected_p[i]
            analysis["comparisons"][condition]["ttest"]["significant_corrected"] = corrected_p[i] < 0.05
            i += 1

    return analysis


def generate_statistical_report(analysis: Dict[str, Any]) -> str:
    """
    Generate a human-readable statistical report.

    Args:
        analysis: Output from analyze_experimental_results

    Returns:
        Formatted string report
    """
    report = []
    report.append("=" * 80)
    report.append("STATISTICAL ANALYSIS REPORT")
    report.append("=" * 80)
    report.append(f"\nMetric: {analysis['metric']}")
    report.append(f"Baseline: {analysis['baseline']}")
    report.append(f"  Mean: {analysis['baseline_mean']:.4f} ± {analysis['baseline_std']:.4f}")
    report.append(f"  95% CI: [{analysis['baseline_ci'][0]:.4f}, {analysis['baseline_ci'][1]:.4f}]")
    report.append(f"  N: {analysis['n_samples']}")

    report.append("\n" + "-" * 80)
    report.append("COMPARISONS TO BASELINE")
    report.append("-" * 80)

    for condition, stats in analysis["comparisons"].items():
        report.append(f"\n{condition}:")
        report.append(f"  Mean: {stats['mean']:.4f} ± {stats['std']:.4f}")
        report.append(f"  95% CI: [{stats['ci'][0]:.4f}, {stats['ci'][1]:.4f}]")
        report.append(f"  Improvement: {stats['improvement_pct']:+.2f}%")

        if "ttest" in stats and "p_value" in stats["ttest"]:
            t = stats["ttest"]
            report.append(f"\n  Paired t-test:")
            report.append(f"    t = {t['t_statistic']:.4f}, p = {t['p_value']:.4f}")
            if "p_value_corrected" in t:
                report.append(f"    p (corrected) = {t['p_value_corrected']:.4f}")
            report.append(f"    Cohen's d = {t['cohens_d']:.4f} ({t['interpretation']})")
            report.append(f"    Significant: {'YES' if t.get('significant_corrected', t['significant']) else 'NO'}")

    report.append("\n" + "=" * 80)
    return "\n".join(report)


def analyze_ablation_study(results_df: pd.DataFrame, metric: str = "trust_score") -> Dict[str, Any]:
    """
    Analyze ablation study results.

    Args:
        results_df: DataFrame with columns 'ablation_condition' and metric columns
        metric: Metric to analyze

    Returns:
        Statistical analysis of ablation effects
    """
    return analyze_experimental_results(
        results_df,
        condition_col="ablation_condition",
        metric_col=metric,
        baseline_condition="full_system"
    )


def analyze_plasticity_over_time(results_df: pd.DataFrame, metric: str = "trust_score") -> Dict[str, Any]:
    """
    Analyze improvement over reasoning cycles (plasticity effect).

    Args:
        results_df: DataFrame with 'cycle' and metric columns
        metric: Metric to analyze

    Returns:
        Dict with trend analysis
    """
    cycles = sorted(results_df["cycle"].unique())

    first_cycle = results_df[results_df["cycle"] == cycles[0]][metric].tolist()
    last_cycle = results_df[results_df["cycle"] == cycles[-1]][metric].tolist()

    # Regression analysis
    from scipy.stats import linregress

    all_cycles = results_df["cycle"].tolist()
    all_metrics = results_df[metric].tolist()
    slope, intercept, r_value, p_value, std_err = linregress(all_cycles, all_metrics)

    # Compare first vs last cycle
    improvement_test = paired_ttest(first_cycle, last_cycle)

    return {
        "metric": metric,
        "n_cycles": len(cycles),
        "first_cycle_mean": float(np.mean(first_cycle)),
        "last_cycle_mean": float(np.mean(last_cycle)),
        "improvement_pct": float((np.mean(last_cycle) - np.mean(first_cycle)) / np.mean(first_cycle) * 100),
        "trend_slope": float(slope),
        "trend_r_squared": float(r_value ** 2),
        "trend_p_value": float(p_value),
        "trend_significant": p_value < 0.05,
        "first_vs_last": improvement_test
    }


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="Statistical analysis of evaluation results")
    parser.add_argument("--file", required=True, help="Path to CSV results file")
    parser.add_argument("--analysis", choices=["ablation", "plasticity", "baseline"],
                       default="ablation", help="Type of analysis")
    parser.add_argument("--metric", default="trust_score", help="Metric to analyze")
    parser.add_argument("--output", help="Output file for JSON results")

    args = parser.parse_args()

    df = pd.read_csv(args.file)

    if args.analysis == "ablation":
        analysis = analyze_ablation_study(df, args.metric)
    elif args.analysis == "plasticity":
        analysis = analyze_plasticity_over_time(df, args.metric)
    else:
        analysis = {"error": "Analysis type not implemented"}

    # Print report
    if "comparisons" in analysis:
        print(generate_statistical_report(analysis))
    else:
        print(json.dumps(analysis, indent=2))

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dumps(analysis, f, indent=2)
        print(f"\nResults saved to {args.output}")
