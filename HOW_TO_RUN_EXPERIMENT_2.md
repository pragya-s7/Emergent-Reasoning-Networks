# How to Run Experiment 2: Adaptive vs Static

## Quick Start

### On Windows (PowerShell)
```powershell
# Small test: 5 queries, 3 cycles (~15 API calls, ~8 minutes, ~$0.50)
.\scripts\run_adaptive_vs_static.ps1 -AnthropicKey "YOUR_KEY_HERE" -NQueries 5 -Cycles 3
```

### On Linux/Mac (Bash)
```bash
# Small test: 5 queries, 3 cycles
./scripts/run_adaptive_vs_static.sh YOUR_KEY_HERE 5 3
```

### Manual Python Command
```bash
python scripts/evaluate_adaptive_vs_static.py \
    --anthropic-key YOUR_KEY_HERE \
    --n-queries 5 \
    --cycles 3 \
    --output-dir output
```

## What It Does

This experiment tests whether **Hebbian adaptation improves reasoning** by comparing:

1. **Static Baseline** - Knowledge graph with learning DISABLED (frozen weights)
2. **Adaptive Treatment** - Knowledge graph with learning ENABLED (adapts over time)

Both conditions:
- Start with the same initial knowledge graph
- Receive the same test queries
- Run for the same number of cycles
- Use real Claude Haiku for reasoning

## What You'll Get

### Console Output
```
EXPERIMENT 2: ADAPTIVE vs STATIC COMPARISON
================================================================================

RUNNING BASELINE: Static Graph (No Hebbian)
================================================================================

--- Cycle 1/3 ---

  Query 1/5: What security vulnerabilities exist in ApolloContract?
    Trust: 0.823, Quality: 0.791, Latency: 14.23s

  Query 2/5: Analyze the financial risks in DeFi protocols
    Trust: 0.756, Quality: 0.742, Latency: 12.15s

...

RUNNING TREATMENT: Adaptive Graph (With Hebbian)
================================================================================

--- Cycle 1/3 ---

  Query 1/5: What security vulnerabilities exist in ApolloContract?
    Trust: 0.831, Quality: 0.803, Latency: 13.87s
    Hebbian: +3 edges, 0 emergent

  Query 2/5: Analyze the financial risks in DeFi protocols
    Trust: 0.768, Quality: 0.755, Latency: 12.42s
    Hebbian: +2 edges, 1 emergent

...

ANALYZING RESULTS
================================================================================

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

AVG EDGE STRENGTH:
  Static:      0.623
  Adaptive:    0.718
  Improvement: +15.2%

================================================================================
OVERALL PERFORMANCE IMPROVEMENT: +12.9%
================================================================================

[CLAIM SUPPORTED]
Adaptive graphs outperform static graphs by 12.9%

HEBBIAN MECHANISMS:
--------------------------------------------------------------------------------
Total edges strengthened: 47
Total emergent connections: 8
Final relation count (static): 156
Final relation count (adaptive): 163

[SUCCESS] Summary saved to: output/comparison_summary_20251028_143052.json
```

### Output Files

In `output/` directory:

1. **static_results_TIMESTAMP.csv**
   ```csv
   cycle,query_idx,query,latency,trust_score,retrieval_accuracy,answer_quality,...
   1,0,"What security...",14.23,0.823,0.75,0.791,...
   1,1,"Analyze the...",12.15,0.756,0.68,0.742,...
   ```

2. **adaptive_results_TIMESTAMP.csv**
   ```csv
   cycle,query_idx,query,latency,trust_score,retrieval_accuracy,answer_quality,edges_strengthened,emergent_edges,...
   1,0,"What security...",13.87,0.831,0.76,0.803,3,0,...
   1,1,"Analyze the...",12.42,0.768,0.70,0.755,2,1,...
   ```

3. **comparison_summary_TIMESTAMP.json**
   ```json
   {
     "experiment": "Adaptive vs Static Comparison",
     "overall_improvement_pct": 12.9,
     "verdict": "CLAIM SUPPORTED",
     "claim": "Adaptive graphs outperform static graphs by 12.9%",
     "results": {
       "trust_score": {
         "static_mean": 0.752,
         "adaptive_mean": 0.841,
         "improvement_pct": 11.8
       },
       ...
     }
   }
   ```

4. **adaptive_kg_cycle_N.json** - KG snapshots showing evolution

## For Your Paper

### Claim to Report

> "We compared adaptive knowledge graphs (with Hebbian plasticity) against static baselines across N queries over M cycles. **Adaptive graphs outperformed static graphs by X%** overall (trust score: +Y%, retrieval: +Z%, quality: +W%). The adaptive system strengthened K edges and formed L emergent connections, demonstrating continual learning."

### Use the actual numbers from your results!

Replace:
- `N` = number of queries you tested
- `M` = number of cycles
- `X%` = overall_improvement_pct from summary
- `Y%`, `Z%`, `W%` = specific metric improvements
- `K` = total_edges_strengthened
- `L` = total_emergent_edges

### Tables for Paper

**Table: Adaptive vs Static Performance**

| Metric | Static | Adaptive | Improvement |
|--------|--------|----------|-------------|
| Trust Score | 0.752 | 0.841 | +11.8% |
| Retrieval Accuracy | 0.680 | 0.765 | +12.5% |
| Answer Quality | 0.715 | 0.801 | +12.0% |
| Avg Edge Strength | 0.623 | 0.718 | +15.2% |
| **Overall** | **-** | **-** | **+12.9%** |

### Figures for Paper

1. **Performance over cycles** - Line plot showing trust/quality improving
2. **Metric comparison** - Bar chart of static vs adaptive
3. **Hebbian activity** - Show edges strengthened + emergent connections

## Recommended Configurations

### Quick Sanity Check (2-3 minutes)
```bash
--n-queries 2 --cycles 2
# Just to verify it works before running full eval
```

### Small Test (8-10 minutes, ~$0.50)
```bash
--n-queries 5 --cycles 3
# Good for testing, not enough for strong claims
```

### Paper-Ready Minimal (40-50 minutes, ~$3-5)
```bash
--n-queries 10 --cycles 5
# Minimum for publishable results
```

### Strong Evidence (2-3 hours, ~$10-15)
```bash
--n-queries 20 --cycles 10
# Robust statistical evidence
```

## Troubleshooting

### "No improvement observed"
- **Increase cycles** - Learning needs time to show effect (try 5-10 cycles)
- **Use repeated queries** - Pass `--use-repeated-queries` flag
- **Check KG snapshots** - Verify adaptive KG is actually changing

### "Results look random/noisy"
- **Increase sample size** - Use more queries (20+)
- **Run multiple times** - Try different seeds, average results
- **Check query quality** - Make sure queries are relevant to your KG

### "API errors / rate limits"
- **Slow down** - Add delays between queries
- **Reduce batch size** - Run fewer queries at once
- **Check key** - Ensure API key is valid and has credits

## Cost Breakdown

Each query generates:
- 1 reasoning call to Claude Haiku (~1K-2K tokens)
- 1-3 validation calls to Claude Haiku (~500-1K tokens each)

Approximate costs:
- Small test (5q × 3c × 2): ~30 API calls → **$0.30-0.60**
- Minimal viable (10q × 5c × 2): ~100 API calls → **$2-4**
- Full eval (20q × 10c × 2): ~400 API calls → **$8-16**

## Next Steps

1. **Run small test first** to verify everything works
2. **Inspect output** to ensure quality looks good
3. **Scale up** for paper-ready numbers
4. **Analyze CSVs** in detail (can import to Excel/pandas)
5. **Create visualizations** from the data
6. **Write results section** using actual numbers

---

**Ready to run?** Just execute the PowerShell command at the top with your Anthropic API key!

