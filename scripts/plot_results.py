
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

def plot_results(csv_filepath):
    """Reads plasticity evaluation data and generates plots."""
    if not os.path.exists(csv_filepath):
        print(f"Error: File not found at {csv_filepath}")
        return

    df = pd.read_csv(csv_filepath)

    # --- Plot 1: Emergent Connections --- 
    plt.figure(figsize=(10, 6))
    df['cumulative_emergent'] = df['emergent_connections'].cumsum()
    plt.plot(df['cycle'], df['cumulative_emergent'], marker='o', linestyle='-', color='b')
    plt.title('Emergent Knowledge Formation Over Time', fontsize=16)
    plt.xlabel('Reasoning Cycle', fontsize=12)
    plt.ylabel('Cumulative Emergent Connections', fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    emergent_plot_path = os.path.join(os.path.dirname(csv_filepath), 'emergent_connections_plot.png')
    plt.savefig(emergent_plot_path)
    print(f"Saved emergent connections plot to {emergent_plot_path}")

    # --- Plot 2: Average Edge Strength ---
    plt.figure(figsize=(10, 6))
    plt.plot(df['cycle'], df['avg_top_k_strength'], marker='s', linestyle='-', color='r')
    plt.title('Knowledge Consolidation: Edge Strength Over Time', fontsize=16)
    plt.xlabel('Reasoning Cycle', fontsize=12)
    plt.ylabel('Average Strength of Top 10 Edges', fontsize=12)
    plt.ylim(0, 1.1) # Strength is capped at 1.0
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    strength_plot_path = os.path.join(os.path.dirname(csv_filepath), 'knowledge_strength_plot.png')
    plt.savefig(strength_plot_path)
    print(f"Saved knowledge strength plot to {strength_plot_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot evaluation results from a CSV file.")
    parser.add_argument("--file", required=True, help="Path to the evaluation results CSV file.")
    args = parser.parse_args()
    plot_results(args.file)
