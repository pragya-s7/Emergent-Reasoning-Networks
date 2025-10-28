#!/bin/bash
# Run Experiment 2: Adaptive vs Static Comparison
# Tests whether Hebbian adaptation improves reasoning performance

set -e

# check if API key provided
if [ -z "$1" ]; then
    echo "Usage: ./run_adaptive_vs_static.sh YOUR_ANTHROPIC_KEY [n_queries] [cycles]"
    echo ""
    echo "Example: ./run_adaptive_vs_static.sh sk-ant-xxx 5 3"
    echo "  - Tests 5 queries"
    echo "  - Runs 3 cycles each"
    echo "  - Compares static vs adaptive graphs"
    exit 1
fi

ANTHROPIC_KEY=$1
N_QUERIES=${2:-5}   # default: 5 queries
CYCLES=${3:-3}      # default: 3 cycles

export TOKENIZERS_PARALLELISM=false

echo "================================================================================"
echo "EXPERIMENT 2: ADAPTIVE vs STATIC COMPARISON"
echo "================================================================================"
echo ""
echo "Configuration:"
echo "  Queries: ${N_QUERIES}"
echo "  Cycles: ${CYCLES}"
echo "  Model: Claude 3 Haiku"
echo "  Estimated runtime: ~$((N_QUERIES * CYCLES * 2)) queries (~$((N_QUERIES * CYCLES * 30 / 60)) minutes)"
echo ""
echo "This experiment compares:"
echo "  [BASELINE]  Static graph (no Hebbian learning)"
echo "  [TREATMENT] Adaptive graph (with Hebbian learning)"
echo ""
echo "================================================================================"
echo ""

python scripts/evaluate_adaptive_vs_static.py \
    --anthropic-key ${ANTHROPIC_KEY} \
    --n-queries ${N_QUERIES} \
    --cycles ${CYCLES} \
    --output-dir output \
    --seed 42

echo ""
echo "================================================================================"
echo "EXPERIMENT COMPLETE!"
echo "================================================================================"
echo ""
echo "Check output/ directory for results:"
echo "  - static_results_*.csv"
echo "  - adaptive_results_*.csv"
echo "  - comparison_summary_*.json"
echo "  - adaptive_kg_cycle_*.json"
echo ""

