"""
Benchmark Runner - Executes code and visualizes performance
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from typing import Dict, Tuple, Optional

from setup_environment import run_benchmark


def execute_and_benchmark(python_code, cpp_code, java_code, rust_code):
    """
    Execute all code versions in Docker and create performance comparison
    
    Returns:
        tuple: (matplotlib_figure, results_markdown)
    """
    # Run benchmark in Docker
    results = run_benchmark(python_code, cpp_code, java_code, rust_code)
    
    # Check for errors
    if "error" in results and not any(k in results for k in ['python', 'cpp', 'java', 'rust']):
        error_msg = f"### Benchmark Error\n\n```\n{results['error']}\n```"
        return None, error_msg
    
    lang_data = _extract_language_data(results)

    figure = _create_performance_chart(lang_data)

    markdown = _generate_results_report(lang_data, results)

    return figure, markdown
    
    


def _extract_language_data(results: Dict) -> list:
    lang_config = {
        'python': {'name': 'Python', 'color': '#3776ab'},
        'cpp': {'name': 'C++', 'color': '#00599C'},
        'java': {'name': 'Java', 'color': '#007396'},
        'rust': {'name': 'Rust', 'color': '#f74c00'}
    }
    
    lang_data = []
    
    for lang_key, config in lang_config.items():
        if lang_key in results:
            result = results[lang_key]
            
            if result.get('success', False):
                lang_data.append({
                    'name': config['name'],
                    'time': result.get('execution_time', 0) * 1000, 
                    'color': config['color'],
                    'status': 'PASS',
                    'output': result.get('output', '')
                })
            else:
                lang_data.append({
                    'name': config['name'],
                    'time': 0,
                    'color': '#666666',
                    'status': 'FAIL',
                    'error': result.get('error', 'Unknown error')
                })
    
    # Sort by execution time DESCENDING (slowest first for left-to-right display)
    lang_data.sort(key=lambda x: x['time'] if x['time'] > 0 else float('inf'), reverse=True)
    
    return lang_data


def _create_performance_chart(lang_data: list) -> Optional[plt.Figure]:
    languages = [item['name'] for item in lang_data]
    times = [item['time'] for item in lang_data]
    colors = [item['color'] for item in lang_data]
    
    if not any(t > 0 for t in times):
        return None
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.set_yscale('log')
    
    bars = ax.bar(languages, times, color=colors, alpha=0.85, 
                   edgecolor='#2c3e50', linewidth=2.5, width=0.6)
    
    if len(times) > 1:
        import numpy as np
        x_positions = np.arange(len(languages))
        valid_times = [t if t > 0 else None for t in times]
        ax.plot(x_positions, valid_times, 'r-', linewidth=3, alpha=0.7, zorder=5)
    
    ax.set_ylabel('Execution Time (ms) - Log Scale', fontsize=13, fontweight='bold')
    ax.set_xlabel('Language', fontsize=13, fontweight='bold')
    ax.set_title('Performance Comparison', fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.25, linestyle='--', which='both')
    ax.grid(axis='y', alpha=0.4, linestyle='-', which='major', linewidth=1)
    
    for bar, time in zip(bars, times):
        if time > 0:
            label = f'{time:.2f}ms'
            ax.text(bar.get_x() + bar.get_width()/2, time * 1.5,
                   label, ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    def format_ms(y, p):
        if y >= 1000:
            return f'{y/1000:.1f}s'
        elif y >= 1:
            return f'{y:.0f}ms'
        else:
            return f'{y:.2f}ms'
    
    ax.yaxis.set_major_formatter(FuncFormatter(format_ms))
    
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    plt.xticks(rotation=0, fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    
    return fig


def _generate_results_report(lang_data: list, raw_results: Dict) -> str:
    markdown_lines = []
    
    python_time = next((item['time'] for item in lang_data 
                       if item['name'] == 'Python' and item['status'] == 'PASS'), None)
    
    successful = [item for item in lang_data if item['status'] == 'PASS' and item['time'] > 0]
    successful_sorted = sorted(successful, key=lambda x: x['time'])
    
    if successful_sorted and python_time and python_time > 0:
        markdown_lines.append("### Performance Ranking\n\n")
        
        for rank, item in enumerate(successful_sorted, 1):
            speedup = python_time / item['time'] if item['time'] > 0 else 0
            
            if rank == 1:
                markdown_lines.append(f"**RANK {rank} - WINNER: {item['name']}**\n")
                markdown_lines.append(f"```\n")
                markdown_lines.append(f"Execution Time: {item['time']:.2f}ms\n")
                if item['name'] != 'Python':
                    markdown_lines.append(f"Speedup: {speedup:.2f}x faster than Python\n")
                else:
                    markdown_lines.append(f"Baseline Performance\n")
                markdown_lines.append(f"```\n\n")
            else:
                markdown_lines.append(f"**RANK {rank}: {item['name']}**\n")
                markdown_lines.append(f"- Execution Time: {item['time']:.2f}ms\n")
                if item['name'] != 'Python':
                    markdown_lines.append(f"- Speedup: {speedup:.2f}x faster than Python\n")
                else:
                    markdown_lines.append(f"- Baseline Performance\n")
                markdown_lines.append("\n")
        
        markdown_lines.append("---\n\n")
        markdown_lines.append("### Execution Details\n\n")
        
        for item in lang_data:
            markdown_lines.append(f"**{item['name']}:**\n")
            
            if item['status'] == 'PASS':
                output = item.get('output', 'No output')
                if len(output) > 300:
                    output = output[:300] + "..."
                markdown_lines.append(f"```\n{output}\n```\n\n")
            else:
                error = item.get('error', 'Unknown error')
                markdown_lines.append(f"```\nERROR: {error[:200]}\n```\n\n")
    
    else:
        markdown_lines.append("### Benchmark Results\n\n")
        markdown_lines.append("**No successful executions**\n\n")
        markdown_lines.append("All languages failed to execute. Check the code for errors.\n\n")
        
        markdown_lines.append("### Execution Details\n\n")
        for item in lang_data:
            error = item.get('error', 'Unknown error')
            markdown_lines.append(f"**{item['name']}:** {error[:200]}\n\n")
    
    return ''.join(markdown_lines)    