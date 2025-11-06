"""
Visualize comparison of different greedy strategies.

Creates a comprehensive comparison chart showing how different
greedy approaches perform on the same datasets.
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from greedy.algorithm import EVChargingScheduler, generate_test_data
from greedy.alternative_strategies import (
    EarliestStartTimeScheduler,
    ShortestDurationScheduler,
    LatestStartTimeScheduler,
    FewestConflictsScheduler,
    MaxWeightedScheduler,
    compare_all_strategies
)


def visualize_strategy_comparison(num_trials=20, dataset_size=200, seed=42):
    """
    Create comprehensive visualization comparing all strategies.
    
    Args:
        num_trials: Number of random datasets to test
        dataset_size: Size of each dataset
        seed: Base random seed
    """
    strategy_results = defaultdict(list)
    
    print(f"Running {num_trials} trials with n={dataset_size}...")
    
    for trial in range(num_trials):
        sessions = generate_test_data(dataset_size, seed=seed + trial)
        optimal_scheduler = EVChargingScheduler()
        results = compare_all_strategies(sessions, optimal_scheduler)
        
        for name, data in results.items():
            strategy_results[name].append(data["selected"])
        
        if (trial + 1) % 5 == 0:
            print(f"  Completed {trial + 1}/{num_trials} trials")
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 10))
    
    # Subplot 1: Box plot comparison
    ax1 = plt.subplot(2, 3, 1)
    strategy_names = list(strategy_results.keys())
    strategy_data = [strategy_results[name] for name in strategy_names]
    
    bp = ax1.boxplot(strategy_data, labels=[name.replace(' ', '\n') for name in strategy_names],
                     patch_artist=True)
    
    # Color the optimal strategy differently
    for i, patch in enumerate(bp['boxes']):
        if 'Optimal' in strategy_names[i]:
            patch.set_facecolor('lightgreen')
        else:
            patch.set_facecolor('lightcoral')
    
    ax1.set_ylabel('Sessions Selected', fontsize=11, fontweight='bold')
    ax1.set_title('Strategy Comparison (Box Plot)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', labelsize=8)
    
    # Subplot 2: Average performance bar chart
    ax2 = plt.subplot(2, 3, 2)
    averages = [np.mean(strategy_results[name]) for name in strategy_names]
    colors = ['green' if 'Optimal' in name else 'red' for name in strategy_names]
    
    bars = ax2.bar(range(len(strategy_names)), averages, color=colors, alpha=0.6, edgecolor='black')
    ax2.set_xticks(range(len(strategy_names)))
    ax2.set_xticklabels([name.replace(' ', '\n') for name in strategy_names], 
                        rotation=0, ha='center', fontsize=8)
    ax2.set_ylabel('Average Sessions Selected', fontsize=11, fontweight='bold')
    ax2.set_title('Average Performance', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    # Subplot 3: Optimality gap
    ax3 = plt.subplot(2, 3, 3)
    optimal_avg = np.mean(strategy_results["Optimal (Earliest Finish)"])
    gaps = [(optimal_avg - np.mean(strategy_results[name])) for name in strategy_names]
    
    bars = ax3.barh(range(len(strategy_names)), gaps, 
                    color=['green' if g == 0 else 'red' for g in gaps],
                    alpha=0.6, edgecolor='black')
    ax3.set_yticks(range(len(strategy_names)))
    ax3.set_yticklabels(strategy_names, fontsize=9)
    ax3.set_xlabel('Sessions Below Optimal', fontsize=11, fontweight='bold')
    ax3.set_title('Optimality Gap', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    ax3.axvline(x=0, color='black', linestyle='-', linewidth=1)
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        if width > 0:
            ax3.text(width, bar.get_y() + bar.get_height()/2.,
                    f'-{width:.1f}', ha='left', va='center', fontsize=8)
    
    # Subplot 4: Performance over trials (line plot)
    ax4 = plt.subplot(2, 3, 4)
    for name in strategy_names:
        style = '-' if 'Optimal' in name else '--'
        linewidth = 2.5 if 'Optimal' in name else 1.5
        ax4.plot(range(num_trials), strategy_results[name], 
                label=name, linestyle=style, linewidth=linewidth, alpha=0.7)
    
    ax4.set_xlabel('Trial Number', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Sessions Selected', fontsize=11, fontweight='bold')
    ax4.set_title('Performance Across Trials', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=7, loc='best')
    ax4.grid(True, alpha=0.3)
    
    # Subplot 5: Success rate (percentage of optimal)
    ax5 = plt.subplot(2, 3, 5)
    optimal_avg = np.mean(strategy_results["Optimal (Earliest Finish)"])
    percentages = [(np.mean(strategy_results[name]) / optimal_avg) * 100 
                   for name in strategy_names]
    
    bars = ax5.bar(range(len(strategy_names)), percentages,
                   color=['green' if p >= 99.5 else 'orange' if p >= 90 else 'red' 
                          for p in percentages],
                   alpha=0.6, edgecolor='black')
    ax5.set_xticks(range(len(strategy_names)))
    ax5.set_xticklabels([name.replace(' ', '\n') for name in strategy_names],
                        rotation=0, ha='center', fontsize=8)
    ax5.set_ylabel('% of Optimal', fontsize=11, fontweight='bold')
    ax5.set_title('Success Rate', fontsize=12, fontweight='bold')
    ax5.axhline(y=100, color='black', linestyle='--', linewidth=1, label='Optimal')
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.set_ylim([0, 110])
    
    # Add percentage labels
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Subplot 6: Statistical summary table
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    table_data = []
    table_data.append(['Strategy', 'Avg', 'Min', 'Max', 'Std', '% Opt'])
    
    for name in strategy_names:
        data = strategy_results[name]
        avg = np.mean(data)
        min_val = np.min(data)
        max_val = np.max(data)
        std_val = np.std(data)
        pct_opt = (avg / optimal_avg) * 100
        
        # Shorten name for table
        short_name = name.replace('Optimal (', '').replace(')', '').replace(' Time', '')
        if len(short_name) > 15:
            short_name = short_name[:15]
        
        table_data.append([
            short_name,
            f'{avg:.1f}',
            f'{min_val}',
            f'{max_val}',
            f'{std_val:.2f}',
            f'{pct_opt:.1f}%'
        ])
    
    table = ax6.table(cellText=table_data, cellLoc='center', loc='center',
                      colWidths=[0.25, 0.12, 0.12, 0.12, 0.12, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Color header row
    for i in range(6):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Color optimal row
    table[(1, 0)].set_facecolor('#C8E6C9')
    
    ax6.set_title('Statistical Summary', fontsize=12, fontweight='bold', pad=20)
    
    plt.suptitle(f'Greedy Strategy Comparison\n{num_trials} trials, n={dataset_size} sessions each',
                fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0.01, 1, 0.96])
    
    # Save figure
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'report', 'figures', 'greedy_strategy_comparison.png'
    )
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Figure saved to: {output_path}")
    
    plt.show()
    
    return strategy_results


if __name__ == "__main__":
    print("="*80)
    print("VISUALIZING GREEDY STRATEGY COMPARISON")
    print("="*80)
    
    results = visualize_strategy_comparison(num_trials=20, dataset_size=200, seed=42)
    
    print("\n" + "="*80)
    print("SUMMARY ANALYSIS")
    print("="*80)
    
    optimal_avg = np.mean(results["Optimal (Earliest Finish)"])
    print(f"\nOptimal (Earliest Finish): {optimal_avg:.2f} sessions (average)")
    
    print("\nSuboptimal strategies:")
    for name, data in results.items():
        if "Optimal" not in name:
            avg = np.mean(data)
            deficit = optimal_avg - avg
            pct = (avg / optimal_avg) * 100
            print(f"  {name:30s}: {avg:5.1f} sessions ({pct:5.1f}% of optimal, -{deficit:.1f})")
    
    print("\n✅ Visualization complete!")
    print("   This empirically demonstrates why 'Earliest Finish Time' is optimal.")
