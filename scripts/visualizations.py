"""
Comprehensive Visualization Suite for Kairos Evaluation Results.

Generates publication-quality plots for:
1. Hebbian plasticity effects (edge strengthening, emergent connections)
2. Ablation study results
3. Validation effectiveness
4. Baseline comparisons
5. Learning curves
6. Statistical summaries
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json

# Set publication-quality style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.figsize'] = (10, 6)


def plot_plasticity_learning_curves(csv_path: str, output_dir: str):
    """
    Plot learning curves showing improvement over reasoning cycles.

    Creates 4 subplots:
    1. Trust score over cycles
    2. Edge strength evolution
    3. Emergent connections formation
    4. Latency changes
    """
    df = pd.read_csv(csv_path)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Hebbian Plasticity: Learning Curves Over Reasoning Cycles', fontsize=14, fontweight='bold')

    # 1. Trust Score
    cycle_trust = df.groupby('cycle')['trust_score'].agg(['mean', 'std', 'sem'])
    axes[0, 0].plot(cycle_trust.index, cycle_trust['mean'], marker='o', linewidth=2, color='#2E86AB')
    axes[0, 0].fill_between(cycle_trust.index,
                            cycle_trust['mean'] - cycle_trust['sem'],
                            cycle_trust['mean'] + cycle_trust['sem'],
                            alpha=0.3, color='#2E86AB')
    axes[0, 0].set_xlabel('Reasoning Cycle')
    axes[0, 0].set_ylabel('Trust Score')
    axes[0, 0].set_title('Trust Score Improvement')
    axes[0, 0].grid(True, alpha=0.3)

    # Add trend line
    z = np.polyfit(cycle_trust.index, cycle_trust['mean'], 1)
    p = np.poly1d(z)
    axes[0, 0].plot(cycle_trust.index, p(cycle_trust.index), "--", color='red', alpha=0.5, label='Trend')
    axes[0, 0].legend()

    # 2. Edge Strength
    if 'avg_top_k_strength' in df.columns:
        cycle_strength = df.groupby('cycle')['avg_top_k_strength'].agg(['mean', 'std', 'sem'])
        axes[0, 1].plot(cycle_strength.index, cycle_strength['mean'], marker='s', linewidth=2, color='#A23B72')
        axes[0, 1].fill_between(cycle_strength.index,
                                cycle_strength['mean'] - cycle_strength['sem'],
                                cycle_strength['mean'] + cycle_strength['sem'],
                                alpha=0.3, color='#A23B72')
        axes[0, 1].set_xlabel('Reasoning Cycle')
        axes[0, 1].set_ylabel('Average Edge Strength')
        axes[0, 1].set_title('Knowledge Consolidation (Edge Strengthening)')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_ylim(0, 1.0)

    # 3. Emergent Connections
    if 'emergent_edges_count' in df.columns:
        cycle_emergent = df.groupby('cycle')['emergent_edges_count'].sum()
        cumulative_emergent = cycle_emergent.cumsum()
        axes[1, 0].plot(cumulative_emergent.index, cumulative_emergent.values,
                       marker='^', linewidth=2, color='#F18F01')
        axes[1, 0].set_xlabel('Reasoning Cycle')
        axes[1, 0].set_ylabel('Cumulative Emergent Connections')
        axes[1, 0].set_title('Emergent Knowledge Formation')
        axes[1, 0].grid(True, alpha=0.3)

    # 4. Latency
    if 'latency' in df.columns:
        cycle_latency = df.groupby('cycle')['latency'].agg(['mean', 'std', 'sem'])
        axes[1, 1].plot(cycle_latency.index, cycle_latency['mean'], marker='D', linewidth=2, color='#C73E1D')
        axes[1, 1].fill_between(cycle_latency.index,
                                cycle_latency['mean'] - cycle_latency['sem'],
                                cycle_latency['mean'] + cycle_latency['sem'],
                                alpha=0.3, color='#C73E1D')
        axes[1, 1].set_xlabel('Reasoning Cycle')
        axes[1, 1].set_ylabel('Latency (seconds)')
        axes[1, 1].set_title('Query Processing Time')
        axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = Path(output_dir) / 'plasticity_learning_curves.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


def plot_ablation_results(csv_path: str, output_dir: str):
    """
    Create bar chart comparing ablation conditions.
    """
    df = pd.read_csv(csv_path)

    # Calculate mean and sem for each ablation condition
    ablation_stats = df.groupby('ablation_condition')['trust_score'].agg(['mean', 'sem', 'count'])
    ablation_stats = ablation_stats.sort_values('mean', ascending=False)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#2E86AB' if idx == 'full_system' else '#A8DADC'
              for idx in ablation_stats.index]

    bars = ax.bar(range(len(ablation_stats)), ablation_stats['mean'],
                  yerr=ablation_stats['sem'], capsize=5, color=colors,
                  edgecolor='black', linewidth=1.5)

    # Highlight full system
    bars[ablation_stats.index.tolist().index('full_system') if 'full_system' in ablation_stats.index.tolist() else 0].set_color('#2E86AB')

    ax.set_xlabel('Ablation Condition', fontweight='bold')
    ax.set_ylabel('Mean Trust Score', fontweight='bold')
    ax.set_title('Ablation Study: Component Contribution Analysis', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(ablation_stats)))
    ax.set_xticklabels([label.replace('_', ' ').title() for label in ablation_stats.index],
                       rotation=45, ha='right')
    ax.grid(True, axis='y', alpha=0.3)

    # Add value labels on bars
    for i, (idx, row) in enumerate(ablation_stats.iterrows()):
        ax.text(i, row['mean'] + row['sem'] + 0.02, f"{row['mean']:.3f}",
               ha='center', va='bottom', fontweight='bold', fontsize=9)

    plt.tight_layout()
    output_path = Path(output_dir) / 'ablation_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


def plot_validation_effectiveness(csv_path: str, output_dir: str):
    """
    Plot validation scores for standard vs noisy reasoning modules.
    """
    df = pd.read_csv(csv_path)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Validation Framework Effectiveness', fontsize=14, fontweight='bold')

    # Box plot of trust scores
    module_types = df['module_type'].unique()
    data_to_plot = [df[df['module_type'] == mt]['trust_score'].values for mt in module_types]

    bp = axes[0].boxplot(data_to_plot, labels=[mt.replace('_', ' ').title() for mt in module_types],
                        patch_artist=True, notch=True)

    # Color boxes
    colors = ['#2E86AB', '#E63946', '#F77F00']
    for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    axes[0].set_ylabel('Trust Score', fontweight='bold')
    axes[0].set_xlabel('Module Type', fontweight='bold')
    axes[0].set_title('Trust Score Distribution by Module Type')
    axes[0].grid(True, axis='y', alpha=0.3)

    # Validation component scores
    validation_metrics = ['logical_score', 'grounding_score', 'novelty_score', 'alignment_score']
    module_comparison = {}

    for mt in module_types:
        subset = df[df['module_type'] == mt]
        module_comparison[mt] = [subset[metric].mean() for metric in validation_metrics]

    x = np.arange(len(validation_metrics))
    width = 0.25

    for i, (mt, scores) in enumerate(module_comparison.items()):
        axes[1].bar(x + i * width, scores, width, label=mt.replace('_', ' ').title(),
                   alpha=0.8)

    axes[1].set_ylabel('Mean Validation Score', fontweight='bold')
    axes[1].set_xlabel('Validation Dimension', fontweight='bold')
    axes[1].set_title('Validation Scores by Dimension')
    axes[1].set_xticks(x + width)
    axes[1].set_xticklabels([m.replace('_score', '').title() for m in validation_metrics])
    axes[1].legend()
    axes[1].grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    output_path = Path(output_dir) / 'validation_effectiveness.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


def plot_baseline_comparison(baseline_results: dict, output_dir: str):
    """
    Compare Kairos against baseline systems.

    Args:
        baseline_results: Dict with structure {baseline_name: {metric: value}}
    """
    metrics = ['trust_score', 'accuracy', 'latency']
    baselines = list(baseline_results.keys())

    fig, ax = plt.subplots(figsize=(12, 6))

    # Normalize metrics to 0-1 scale for comparison
    normalized_data = {}
    for baseline in baselines:
        normalized_data[baseline] = []
        for metric in metrics:
            value = baseline_results[baseline].get(metric, 0)
            # Normalize (invert for latency)
            if metric == 'latency':
                norm_value = 1 - min(value / 10.0, 1.0)  # Lower is better
            else:
                norm_value = value
            normalized_data[baseline].append(norm_value)

    x = np.arange(len(metrics))
    width = 0.18
    colors = ['#2E86AB', '#F77F00', '#E63946', '#06A77D']

    for i, baseline in enumerate(baselines):
        ax.bar(x + i * width, normalized_data[baseline], width,
              label=baseline.replace('_', ' ').title(), color=colors[i % len(colors)], alpha=0.8)

    ax.set_ylabel('Normalized Score', fontweight='bold')
    ax.set_xlabel('Metric', fontweight='bold')
    ax.set_title('Baseline Comparison: Kairos vs Alternative Approaches', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width * (len(baselines) - 1) / 2)
    ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics])
    ax.legend(loc='upper right')
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    output_path = Path(output_dir) / 'baseline_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


def plot_edge_strength_heatmap(kg_snapshots: list, output_dir: str):
    """
    Create heatmap showing edge strength evolution over cycles.

    Args:
        kg_snapshots: List of paths to KG JSON files at different cycles
    """
    # Load KG snapshots
    edge_evolution = {}

    for i, snapshot_path in enumerate(kg_snapshots):
        with open(snapshot_path, 'r') as f:
            kg_data = json.load(f)

        for rel in kg_data.get('relations', []):
            # Get entity labels
            subj_id = rel['subject_id']
            obj_id = rel['object_id']

            # Find entity labels
            subj_label = next((e['label'] for e in kg_data['entities'] if e['id'] == subj_id), subj_id)
            obj_label = next((e['label'] for e in kg_data['entities'] if e['id'] == obj_id), obj_id)

            edge_key = f"{subj_label}→{obj_label}"

            if edge_key not in edge_evolution:
                edge_evolution[edge_key] = []

            edge_evolution[edge_key].append(rel.get('confidence', 0))

    # Create heatmap data
    edges = list(edge_evolution.keys())[:15]  # Top 15 edges
    cycles = list(range(len(kg_snapshots)))

    heatmap_data = np.zeros((len(edges), len(cycles)))

    for i, edge in enumerate(edges):
        strengths = edge_evolution[edge]
        for j in range(min(len(strengths), len(cycles))):
            heatmap_data[i, j] = strengths[j]

    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(cycles)
    ax.set_yticks(range(len(edges)))
    ax.set_xticklabels([f'Cycle {c+1}' for c in cycles])
    ax.set_yticklabels(edges, fontsize=8)
    ax.set_xlabel('Reasoning Cycle', fontweight='bold')
    ax.set_ylabel('Knowledge Graph Edge', fontweight='bold')
    ax.set_title('Edge Strength Evolution (Hebbian Consolidation)', fontsize=14, fontweight='bold')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Edge Strength', rotation=270, labelpad=20, fontweight='bold')

    plt.tight_layout()
    output_path = Path(output_dir) / 'edge_strength_heatmap.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


def create_all_visualizations(plasticity_csv: str = None,
                              ablation_csv: str = None,
                              validation_csv: str = None,
                              kg_snapshots: list = None,
                              output_dir: str = "output/figures"):
    """
    Generate all visualizations for the paper.

    Args:
        plasticity_csv: Path to plasticity evaluation results
        ablation_csv: Path to ablation study results
        validation_csv: Path to validation evaluation results
        kg_snapshots: List of KG snapshot paths
        output_dir: Where to save figures
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("GENERATING PUBLICATION-QUALITY VISUALIZATIONS")
    print("="*80)

    if plasticity_csv:
        print("\n1. Plasticity learning curves...")
        plot_plasticity_learning_curves(plasticity_csv, output_dir)

    if ablation_csv:
        print("\n2. Ablation study results...")
        plot_ablation_results(ablation_csv, output_dir)

    if validation_csv:
        print("\n3. Validation effectiveness...")
        plot_validation_effectiveness(validation_csv, output_dir)

    if kg_snapshots:
        print("\n4. Edge strength heatmap...")
        plot_edge_strength_heatmap(kg_snapshots, output_dir)

    print("\n" + "="*80)
    print(f"All visualizations saved to {output_dir}/")
    print("="*80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Kairos evaluation visualizations")
    parser.add_argument("--plasticity-results", help="Path to plasticity CSV")
    parser.add_argument("--ablation-results", help="Path to ablation CSV")
    parser.add_argument("--validation-results", help="Path to validation CSV")
    parser.add_argument("--kg-snapshots", nargs='+', help="Paths to KG snapshots")
    parser.add_argument("--output-dir", default="output/figures", help="Output directory")

    args = parser.parse_args()

    create_all_visualizations(
        plasticity_csv=args.plasticity_results,
        ablation_csv=args.ablation_results,
        validation_csv=args.validation_results,
        kg_snapshots=args.kg_snapshots,
        output_dir=args.output_dir
    )
