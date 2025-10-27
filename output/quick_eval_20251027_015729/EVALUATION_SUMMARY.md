# Kairos Quick Evaluation Summary (Option A)

**Generated:** Mon Oct 27 02:56:15 EDT 2025
**Run ID:** 20251027_015729

## Configuration
- Validation questions: 10
- Ablation questions: 15
- Plasticity cycles: 5
- Baseline questions: 10
- Total API calls: ~200

## Output Files

### Results CSVs
- Baseline comparison: `baseline_comparison_results_*.csv`
- Validation effectiveness: `validation_evaluation_results_*.csv`
- Ablation study: `ablation_evaluation_results_*.csv`
- Plasticity evaluation: `plasticity_evaluation_results_*.csv`

### Visualizations
All figures saved to: `figures/`
- `baseline_comparison.png`
- `validation_effectiveness.png`
- `ablation_comparison.png`
- `plasticity_learning_curves.png`
- `edge_strength_heatmap.png`

## Next Steps for Paper

1. **Review Results**: Check all CSV files for your actual numbers
2. **Use Figures**: Copy figures from `figures/` directory to paper
3. **Write Results Section**: Use the statistical outputs from each evaluation
4. **Discussion**: Interpret findings in context of your research questions

## Key Metrics to Report

From baseline_comparison:
- Kairos vs Naive KG: Improvement %, p-value
- Kairos vs Single Agent: Improvement %, p-value
- Kairos vs No Validation: Improvement %, p-value

From validation_evaluation:
- Detection rate for logical fallacies
- Detection rate for hallucinations
- Standard vs Noisy: t-statistic, p-value

From ablation_evaluation:
- Full system trust score
- Impact of removing validation (%)
- Impact of removing Hebbian (%)

From plasticity_evaluation:
- Cycle 1 vs Cycle 5 improvement
- Number of emergent connections formed
- Edge strength increase

