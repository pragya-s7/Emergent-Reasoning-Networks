# Experiment 2: Adaptive vs Static Comparison

## Research Question
**Does Hebbian adaptation improve reasoning performance over static knowledge graphs?**

## Experimental Design

### Conditions

1. **BASELINE (Static)**
   - Knowledge graph with Hebbian learning DISABLED
   - Edge weights remain frozen
   - No strengthening, no decay, no emergent connections

2. **TREATMENT (Adaptive)**
   - Knowledge graph with Hebbian learning ENABLED
   - Edge weights adapt based on usage
   - Strengthening of used paths
   - Decay of unused paths
   - Formation of emergent connections

### Methodology

- **Same initial state**: Both conditions start with identical knowledge graphs
- **Same queries**: Both receive the exact same test queries
- **Same cycles**: Queries are repeated over multiple cycles to observe learning
- **Real LLM reasoning**: Uses Claude 3 Haiku for actual reasoning (not simulated)

### Metrics

1. **Trust Score** - Average validation quality
2. **Retrieval Accuracy** - Ability to find relevant facts
3. **Answer Quality** - Reasoning correctness and thoroughness
4. **Edge Strength** - Average strength of top edges

### Expected Outcome

**Hypothesis**: Adaptive graphs will outperform static graphs because:
- Frequently used reasoning paths strengthen → faster, more reliable retrieval
- Weak/unused edges decay → reduced noise
- Emergent connections form → new insights discovered

## Running the Experiment

### Quick Start (Small Test)

```bash
# 5 queries, 3 cycles (~15 API calls, ~8 minutes)
./scripts/run_adaptive_vs_static.sh YOUR_ANTHROPIC_KEY 5 3
```

### Minimal Viable (Paper-Ready)

```bash
# 10 queries, 5 cycles (~100 API calls, ~50 minutes)
./scripts/run_adaptive_vs_static.sh YOUR_ANTHROPIC_KEY 10 5
```

### Full Evaluation

```bash
# 20 queries, 10 cycles (~400 API calls, ~200 minutes)
./scripts/run_adaptive_vs_static.sh YOUR_ANTHROPIC_KEY 20 10
```

### Manual Run with Custom Queries

```python
python scripts/evaluate_adaptive_vs_static.py \
    --anthropic-key YOUR_KEY \
    --queries "What security risks exist?" "Analyze financial metrics" \
    --cycles 3 \
    --output-dir output
```

## Output Files

After running, check `output/` directory:

### CSV Results
- `static_results_TIMESTAMP.csv` - Baseline performance metrics
- `adaptive_results_TIMESTAMP.csv` - Treatment performance metrics

### Knowledge Graph Snapshots
- `adaptive_kg_cycle_1.json` - KG after cycle 1
- `adaptive_kg_cycle_2.json` - KG after cycle 2
- etc.

### Summary
- `comparison_summary_TIMESTAMP.json` - Statistical comparison

## Interpreting Results

### Success Criteria

The claim **"Adaptive graphs outperform static graphs by X%"** is **SUPPORTED** if:
- Overall improvement > 5%
- Trust scores improve
- Edge strengths increase over cycles
- Emergent connections form

### Example Output

```
OVERALL PERFORMANCE IMPROVEMENT: +12.3%

TRUST SCORE:
  Static:      0.752
  Adaptive:    0.841
  Improvement: +11.8%

RETRIEVAL ACCURACY:
  Static:      0.680
  Adaptive:    0.765
  Improvement: +12.5%

ANSWER QUALITY:
  Static:      0.715
  Adaptive:    0.801
  Improvement: +12.0%

HEBBIAN MECHANISMS:
  Total edges strengthened: 47
  Total emergent connections: 8
  Final relation count (static): 156
  Final relation count (adaptive): 163

[CLAIM SUPPORTED]
Adaptive graphs outperform static graphs by 12.3%
```

## For Your Paper

### Results to Report

1. **Performance Improvement**
   ```
   "Adaptive graphs outperformed static graphs by X% overall
   (trust: +Y%, retrieval: +Z%, quality: +W%)"
   ```

2. **Hebbian Mechanisms**
   ```
   "Over N cycles, the adaptive system strengthened M edges
   and formed K emergent connections, while the static baseline
   showed no adaptation."
   ```

3. **Statistical Significance**
   - Run with n_queries ≥ 10, cycles ≥ 5
   - Report means, standard deviations
   - Can compute p-values from the CSVs

### Figure Ideas

1. **Line plot**: Trust score over cycles (static vs adaptive)
2. **Bar chart**: Average performance by metric
3. **Heatmap**: Edge strength evolution
4. **Network diagram**: Emergent connections formed

## Troubleshooting

### "No improvement observed"
- Increase number of cycles (need time for learning to show effect)
- Use repeated queries (tests strengthening of same paths)
- Check that adaptive KG is actually changing (inspect snapshots)

### "API errors"
- Check API key is valid
- Reduce n_queries to avoid rate limits
- Add delays between queries if needed

### "Results are noisy"
- Increase sample size (more queries)
- Run multiple times with different seeds
- Average across runs

## Cost Estimation

- Each query = 2 API calls (1 reasoning + 1 validation)
- Approximate cost: $0.01-0.02 per query pair
- Small test (5 queries × 3 cycles × 2 conditions): ~$1-2
- Full eval (20 queries × 10 cycles × 2 conditions): ~$8-16

## Next Steps

1. Run small test first to verify it works
2. Inspect results to ensure quality
3. Scale up for paper-ready numbers
4. Analyze CSV files for statistical tests
5. Create visualizations from the data

