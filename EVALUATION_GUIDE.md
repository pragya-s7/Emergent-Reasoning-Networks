# Kairos Comprehensive Evaluation Guide

**For NORA 2025 Workshop Submission**

This guide walks you through running the complete, publication-quality evaluation suite for the Kairos system.

## Quick Start

### Prerequisites

```bash
# Ensure Python 3.8+ and pip are installed
python --version

# Install all dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Run Complete Evaluation (Recommended)

Run the entire evaluation pipeline with one command:

```bash
python scripts/run_comprehensive_evaluation.py \
  --anthropic-key $ANTHROPIC_API_KEY \
  --n-validation-questions 20 \
  --n-ablation-questions 30 \
  --plasticity-cycles 10 \
  --queries-per-cycle 5
```

**Expected Runtime:** ~2-4 hours depending on API latency

**Output:** All results will be saved to `output/evaluations/eval_run_TIMESTAMP/`

---

## What Gets Evaluated

### 1. Validation Effectiveness (RQ1)
**Research Question:** Can the multi-dimensional validation framework catch flawed reasoning?

**Test Method:**
- Run 20 questions through standard reasoning modules
- Run same questions through intentionally flawed modules (logical fallacies, hallucinations)
- Compare validation scores

**Expected Result:** Validation scores significantly lower for flawed modules (p < 0.05)

**Output:**
- `validation_evaluation_results_*.csv`
- `figures/validation_effectiveness.png`

---

### 2. Ablation Study (RQ2)
**Research Question:** What is the contribution of each system component?

**Components Tested:**
1. Full system (baseline)
2. No validation layer
3. No Hebbian plasticity
4. No logical validation
5. No grounding validation
6. No novelty validation
7. No alignment validation

**Test Method:**
- Run 30 questions for each ablation condition
- Compare trust scores and performance metrics

**Expected Result:** Trust score degrades when components are removed

**Output:**
- `ablation_evaluation_results_*.csv`
- `ablation_evaluation_results_*_analysis.json`
- `figures/ablation_comparison.png`

---

### 3. Hebbian Plasticity (RQ3)
**Research Question:** Does Hebbian learning improve reasoning over time?

**Test Method:**
- Run 5 repeated queries across 10 reasoning cycles
- Track edge strength evolution
- Monitor emergent connection formation
- Measure performance improvements

**Expected Result:**
- Edge strengths increase for frequently used paths
- Trust scores improve over cycles
- Emergent connections form between co-activated entities

**Output:**
- `plasticity_evaluation_results_*.csv`
- `plasticity_evaluation_results_*_kg_cycle_N.json` (KG snapshots)
- `plasticity_evaluation_results_*_analysis.txt`
- `figures/plasticity_learning_curves.png`
- `figures/edge_strength_heatmap.png`

---

## Running Individual Evaluations

### Validation Effectiveness Only

```bash
python scripts/evaluate_validation_fixed.py \
  --anthropic-key $ANTHROPIC_API_KEY \
  --dataset tests/comprehensive_evaluation_dataset.json \
  --kg-path output/knowledge_graph.json \
  --n-questions 20 \
  --output-dir output
```

### Ablation Study Only

```bash
python scripts/evaluate_ablation_fixed.py \
  --anthropic-key $ANTHROPIC_API_KEY \
  --dataset tests/comprehensive_evaluation_dataset.json \
  --kg-path output/knowledge_graph.json \
  --n-questions 30 \
  --output-dir output
```

### Plasticity Evaluation Only

```bash
python scripts/evaluate_plasticity_fixed.py \
  --anthropic-key $ANTHROPIC_API_KEY \
  --dataset tests/comprehensive_evaluation_dataset.json \
  --kg-path output/knowledge_graph.json \
  --cycles 10 \
  --queries-per-cycle 5 \
  --use-repeated-queries \
  --output-dir output
```

---

## Generating Visualizations

After running evaluations, generate publication-quality figures:

```bash
python scripts/visualizations.py \
  --validation-results output/validation_evaluation_results_*.csv \
  --ablation-results output/ablation_evaluation_results_*.csv \
  --plasticity-results output/plasticity_evaluation_results_*.csv \
  --kg-snapshots output/plasticity_evaluation_results_*_kg_cycle_*.json \
  --output-dir output/figures
```

---

## Understanding the Results

### Key Metrics

1. **Trust Score** (0-1): Aggregate validation quality
   - Computed as: `mean([logical_score, grounding_score, novelty_score, alignment_score])`
   - Higher = better reasoning quality

2. **Validation Scores** (0-1): Individual validation dimensions
   - Logical: Coherence and absence of fallacies
   - Grounding: Claims verified in knowledge graph
   - Novelty: Emergent insights beyond KG
   - Alignment: Respects user preferences

3. **Edge Strength** (0-1): Hebbian consolidation level
   - Increases with usage
   - Decays when unused

4. **Emergent Connections**: New edges formed between co-activated entities

### Statistical Significance

All comparisons include:
- **Paired t-tests** for within-subject comparisons
- **Wilcoxon signed-rank tests** for non-parametric alternative
- **Cohen's d** effect sizes
- **Holm-Bonferroni correction** for multiple comparisons
- **95% confidence intervals** via bootstrap

**Interpretation:**
- p < 0.05: Statistically significant
- Cohen's d: |d| > 0.8 = large effect, 0.5-0.8 = medium, 0.2-0.5 = small

---

## For the Paper

### Essential Results to Report

1. **Validation Effectiveness:**
   ```
   Standard vs Noisy Logical: t(19) = X.XX, p < 0.001, d = X.XX
   Detection rate: XX.X% of flawed reasoning caught
   ```

2. **Ablation Study:**
   ```
   Full system: M = X.XX (SD = X.XX)
   No validation: M = X.XX (SD = X.XX), t(29) = X.XX, p < 0.001, d = X.XX
   No Hebbian: M = X.XX (SD = X.XX), t(29) = X.XX, p < 0.01, d = X.XX
   ```

3. **Plasticity:**
   ```
   Linear trend: β = X.XXX, R² = X.XX, p < 0.001
   Cycle 1 vs Cycle 10: t(4) = X.XX, p < 0.05, d = X.XX
   Improvement: +XX.X%
   Emergent connections: N = XX
   ```

### Figures for Paper

1. **Figure 1:** Plasticity learning curves (4 subplots)
2. **Figure 2:** Ablation comparison (bar chart)
3. **Figure 3:** Validation effectiveness (box plots + grouped bars)
4. **Figure 4:** Edge strength heatmap (optional, if space permits)

---

## Troubleshooting

### Issue: API Rate Limits

**Solution:** Add delays between queries:
```python
# In evaluation scripts, add after each query:
import time
time.sleep(1)  # 1 second delay
```

### Issue: Out of Memory

**Solution:** Reduce number of questions:
```bash
--n-validation-questions 10 \
--n-ablation-questions 15 \
--plasticity-cycles 5
```

### Issue: Scripts Failing

**Solution:** Check dependencies:
```bash
pip install --upgrade anthropic pandas numpy scipy matplotlib seaborn
```

### Issue: Empty Results

**Solution:** Check if KG file exists and is valid:
```bash
python -c "import json; print(json.load(open('output/knowledge_graph.json'))['entities'][:3])"
```

---

## Reproducibility

All scripts use:
- **Random seed:** 42 (default)
- **Temperature:** 0 for LLM calls (deterministic)
- **Fixed evaluation dataset:** `tests/comprehensive_evaluation_dataset.json`

To reproduce results exactly:
```bash
python scripts/run_comprehensive_evaluation.py \
  --anthropic-key $ANTHROPIC_API_KEY \
  --seed 42
```

---

## Customization

### Use Different Dataset

```bash
python scripts/run_comprehensive_evaluation.py \
  --dataset path/to/your/dataset.json \
  --anthropic-key $ANTHROPIC_API_KEY
```

**Dataset Format:**
```json
{
  "evaluation_questions": [
    {
      "id": "q1",
      "question": "Your question here?",
      "expected_conclusion_keywords": ["keyword1", "keyword2"],
      "key_triples": ["Entity1 --relation--> Entity2"],
      "requires_multi_hop": false
    }
  ]
}
```

### Adjust Evaluation Scale

For quick testing (10-15 minutes):
```bash
--n-validation-questions 5 \
--n-ablation-questions 10 \
--plasticity-cycles 3 \
--queries-per-cycle 2
```

For maximum rigor (4-6 hours):
```bash
--n-validation-questions 50 \
--n-ablation-questions 50 \
--plasticity-cycles 20 \
--queries-per-cycle 10
```

---

## Output Directory Structure

```
output/evaluations/eval_run_TIMESTAMP/
├── EVALUATION_REPORT.md                          # Summary report
├── evaluation_results.json                       # Complete results JSON
├── validation_evaluation_results_*.csv           # Validation data
├── ablation_evaluation_results_*.csv             # Ablation data
├── ablation_evaluation_results_*_analysis.json   # Statistical analysis
├── plasticity_evaluation_results_*.csv           # Plasticity data
├── plasticity_evaluation_results_*_analysis.txt  # Plasticity analysis
├── plasticity_evaluation_results_*_kg_cycle_N.json  # KG snapshots
└── figures/                                      # All plots
    ├── validation_effectiveness.png
    ├── ablation_comparison.png
    ├── plasticity_learning_curves.png
    └── edge_strength_heatmap.png
```

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the generated `EVALUATION_REPORT.md` in your output directory
3. Examine the console output for error messages
4. Verify all dependencies are installed: `pip list | grep -E "(anthropic|pandas|scipy|matplotlib)"`

---

## Citation

If you use this evaluation framework, please cite:

```bibtex
@inproceedings{kairos2025,
  title={Kairos: Emergent Reasoning Networks for Multi-Agent Knowledge Graph Validation},
  booktitle={NORA Workshop at NeurIPS},
  year={2025}
}
```

---

**Good luck with your submission! 🚀**
