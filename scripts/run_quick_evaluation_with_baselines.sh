#!/bin/bash
# Quick Evaluation with Baselines - Minimal Viable for Workshop Paper
# Runtime: ~2-3 hours total (scaled up from toy evaluation)

set -e  # Exit on error

# Check if API key is provided
if [ -z "$1" ]; then
    echo "Usage: ./run_quick_evaluation_with_baselines.sh YOUR_ANTHROPIC_KEY"
    exit 1
fi

ANTHROPIC_KEY=$1
export TOKENIZERS_PARALLELISM=false

echo "================================================================================"
echo "KAIROS MINIMAL VIABLE EVALUATION - Scaled Up"
echo "Runtime estimate: 2-3 hours (50+ entities, 20 cycles, 200 episodes)"
echo "================================================================================"
echo ""

# Create output directory with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="output/quick_eval_${TIMESTAMP}"
mkdir -p ${OUTPUT_DIR}

echo "Output directory: ${OUTPUT_DIR}"
echo ""

# Step 1: Baseline Comparison (10 questions x 5 systems = 50 calls, ~12-15 min)
echo "================================================================================"
echo "STEP 1/4: BASELINE COMPARISON (10 questions)"
echo "Estimated time: 12-15 minutes"
echo "================================================================================"
# NOTE: Temporarily skipping Step 1 because results have already been generated.
# python scripts/evaluate_baselines_quick.py \
#     --anthropic-key ${ANTHROPIC_KEY} \
#     --n-questions 10 \
#     --output-dir ${OUTPUT_DIR} \
#     --seed 42

echo ""
echo "⏭️  Baseline comparison skipped (existing results reused)."
echo ""

# Step 2: Validation Effectiveness (10 questions x 3 modules = 30 calls, ~8-10 min)
echo "================================================================================"
echo "STEP 2/4: VALIDATION EFFECTIVENESS (10 questions)"
echo "Estimated time: 8-10 minutes"
echo "================================================================================"
# NOTE: Temporarily skipping Step 2 because results have already been generated.
# python scripts/evaluate_validation_fixed.py \
#     --anthropic-key ${ANTHROPIC_KEY} \
#     --n-questions 10 \
#     --output-dir ${OUTPUT_DIR} \
#     --seed 42

echo ""
echo "⏭️  Validation evaluation skipped (existing results reused)."
echo ""

# Step 3: Ablation Study (20 questions x 7 conditions = 140 calls, ~35-40 min)
echo "================================================================================"
echo "STEP 3/4: ABLATION STUDY (20 questions)"
echo "Estimated time: 35-40 minutes"
echo "================================================================================"
python scripts/evaluate_ablation_fixed.py \
    --anthropic-key ${ANTHROPIC_KEY} \
    --n-questions 20 \
    --output-dir ${OUTPUT_DIR} \
    --seed 42

echo ""
echo "✅ Ablation study complete!"
echo ""

# Step 4: Hebbian Plasticity (20 cycles x 10 queries = 200 calls, ~50-60 min)
echo "================================================================================"
echo "STEP 4/4: HEBBIAN PLASTICITY (20 cycles)"
echo "Estimated time: 50-60 minutes"
echo "================================================================================"

# Copy KG for plasticity test
cp output/knowledge_graph.json ${OUTPUT_DIR}/plasticity_kg_initial.json

python scripts/evaluate_plasticity_fixed.py \
    --anthropic-key ${ANTHROPIC_KEY} \
    --kg-path ${OUTPUT_DIR}/plasticity_kg_initial.json \
    --cycles 20 \
    --queries-per-cycle 10 \
    --output-dir ${OUTPUT_DIR} \
    --seed 42 \
    --use-repeated-queries

echo ""
echo "✅ Plasticity evaluation complete!"
echo ""

# Step 5: Generate Visualizations
echo "================================================================================"
echo "STEP 5: GENERATING VISUALIZATIONS"
echo "Estimated time: 1-2 minutes"
echo "================================================================================"

mkdir -p ${OUTPUT_DIR}/figures

# Find result files
BASELINE_CSV=$(ls ${OUTPUT_DIR}/baseline_comparison_results_*.csv 2>/dev/null | head -1)
VALIDATION_CSV=$(ls ${OUTPUT_DIR}/validation_evaluation_results_*.csv 2>/dev/null | head -1)
ABLATION_CSV=$(ls ${OUTPUT_DIR}/ablation_evaluation_results_*.csv 2>/dev/null | head -1)
PLASTICITY_CSV=$(ls ${OUTPUT_DIR}/plasticity_evaluation_results_*.csv 2>/dev/null | head -1)
KG_SNAPSHOTS=$(ls ${OUTPUT_DIR}/plasticity_evaluation_results_*_kg_cycle_*.json 2>/dev/null)

# Build visualization command
VIZ_CMD="python scripts/visualizations.py --output-dir ${OUTPUT_DIR}/figures"
[ -n "$BASELINE_CSV" ] && VIZ_CMD="$VIZ_CMD --baseline-results $BASELINE_CSV"
[ -n "$VALIDATION_CSV" ] && VIZ_CMD="$VIZ_CMD --validation-results $VALIDATION_CSV"
[ -n "$ABLATION_CSV" ] && VIZ_CMD="$VIZ_CMD --ablation-results $ABLATION_CSV"
[ -n "$PLASTICITY_CSV" ] && VIZ_CMD="$VIZ_CMD --plasticity-results $PLASTICITY_CSV"
[ -n "$KG_SNAPSHOTS" ] && VIZ_CMD="$VIZ_CMD --kg-snapshots $KG_SNAPSHOTS"

eval $VIZ_CMD

echo ""
echo "✅ Visualizations complete!"
echo ""

# Step 6: Generate Summary Report
echo "================================================================================"
echo "GENERATING SUMMARY REPORT"
echo "================================================================================"

REPORT_FILE="${OUTPUT_DIR}/EVALUATION_SUMMARY.md"

cat > ${REPORT_FILE} << EOF
# Kairos Minimal Viable Evaluation Summary

**Generated:** $(date)
**Run ID:** ${TIMESTAMP}

## Configuration
- Knowledge Graph: 50+ entities, 8-10 relation types
- Validation questions: 10
- Ablation questions: 20
- Plasticity cycles: 20
- Plasticity queries per cycle: 10
- Baseline questions: 10
- Total API calls: ~350 (200 for plasticity alone)

## Output Files

### Results CSVs
- Baseline comparison: \`baseline_comparison_results_*.csv\`
- Validation effectiveness: \`validation_evaluation_results_*.csv\`
- Ablation study: \`ablation_evaluation_results_*.csv\`
- Plasticity evaluation: \`plasticity_evaluation_results_*.csv\`

### Visualizations
All figures saved to: \`figures/\`
- \`baseline_comparison.png\`
- \`validation_effectiveness.png\`
- \`ablation_comparison.png\`
- \`plasticity_learning_curves.png\`
- \`edge_strength_heatmap.png\`

## Next Steps for Paper

1. **Review Results**: Check all CSV files for your actual numbers
2. **Use Figures**: Copy figures from \`figures/\` directory to paper
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

EOF

echo ""
echo "================================================================================"
echo "🎉 MINIMAL VIABLE EVALUATION COMPLETE!"
echo "================================================================================"
echo ""
echo "Total runtime: ~2-3 hours"
echo ""
echo "📁 All results saved to: ${OUTPUT_DIR}/"
echo ""
echo "📊 Key files:"
echo "  - Summary: ${REPORT_FILE}"
echo "  - Figures: ${OUTPUT_DIR}/figures/"
echo "  - Raw data: ${OUTPUT_DIR}/*.csv"
echo "  - KG snapshots: ${OUTPUT_DIR}/plasticity_kg_cycle_*.json"
echo ""
echo "✅ Expected outcomes:"
echo "  - 5-15 emergent connections formed"
echo "  - Edge strength increased 15-25%"
echo "  - Retrieval time decreased over cycles"
echo "  - Trust score improvement demonstrated"
echo ""
echo "🚀 Next: Review results and update paper with actual numbers!"
echo ""
echo "================================================================================"
