import os
import io 
import sys
from dotenv import load_dotenv
import subprocess
import asyncio
import concurrent.futures

from openai import OpenAI

import gradio as gr 
from styles import DEFAULT_PYTHON, CUSTOM_CSS
import matplotlib.pyplot as plt

from setup_environment import get_manager, get_system_info, get_compile_command, run_benchmark, cleanup_manager


## Load Env
load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
grok_api_key = os.getenv('GROK_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key loaded SUCCESSFULLY [{openai_api_key[:8]}]")
else:
    print("OpenAI API not found or non existing")
    
if anthropic_api_key:
    print(f"Anthropic API Key loaded SUCCESSFULLY [{anthropic_api_key[:7]}]")
else:
    print("Anthropic API not found or non existing")

if grok_api_key:
    print(f"Grok API Key loaded SUCCESSFULLY [{grok_api_key[:4]}]")
else:
    print("Grok API not found or non existing")


anthropic_url = "https://api.anthropic.com/v1/"
grok_url = "https://api.x.ai/v1"
ollama_url = "http://localhost:11434/v1"

openai = OpenAI()
anthropic = OpenAI(api_key=anthropic_api_key, base_url=anthropic_url)
grok = OpenAI(api_key=grok_api_key, base_url=grok_url)
ollama = OpenAI(api_key="ollama", base_url=ollama_url)

models = ["gpt-5", "claude-sonnet-4-5", "grok-4", "gpt-oss:120b:cloud", "minimax-m2:cloud", "deepseek-v3.2:cloud", "kimi-k2-thinking:cloud"]

clients = {
    "gpt-5": openai,
    "claude-sonnet-4-5": anthropic,
    "grok-4": grok, 
    "gpt-oss:120b:cloud": ollama, 
    "minimax-m2:cloud": ollama, 
    "deepseek-v3.2:cloud": ollama, 
    "kimi-k2-thinking:cloud": ollama
}


## LLM interraction
def system_prompt(language):
    return f"""
            Your task is to convert Python code into high performance {language} code.
            Respond only with {language} code. Do not provide any explanation other than occasional comments.
            The {language} response needs to produce an identical output in the fastest possible time.
        """

def user_prompt_for(python, porting_lang):
    system_info = get_system_info()
    compile_command = get_compile_command(porting_lang)
    
    return f"""
            Port this Python code to {porting_lang} with the fastest possible implementation that produces identical output in the least time.
            The system information is:
            {system_info}
            Your response will be written to a file and then compiled and executed; the compilation command is:
            {compile_command}
            Respond only with {porting_lang} code.
            Python code to port:

            ```python
            {python}
            ```
        """

def messages(python, language):
    return [
        {"role": "system", "content": system_prompt(language)},
        {"role": "user", "content": user_prompt_for(python, language)},
    ]

def porting(model, python, port_language): 
    client = clients[model]
    reasoning_effort = "high" if "gpt" in model else None

    response = client.chat.completions.create(
        model=model, 
        messages=messages(python, port_language), 
        reasoning_effort=reasoning_effort
    )
    reply = response.choices[0].message.content
    reply = reply.replace('```cpp','').replace('```rust','').replace('```java','').replace('```','')

    return reply

def port_all_languages(python_code, model):
    languages = ["C++", "Java", "Rust"]

    if not python_code.strip():
        return "// No Python code provided", "// No Python code provided", "// No Python code provided"
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            lang: executor.submit(porting, model, python_code, lang) for lang in languages
        }

        results = {}
        for lang, future in futures.items():
            try:
                results[lang] = future.result(timeout=120)
            except Exception as e:
                results[lang] = f"// Error porting to {lang}: {str(e)}"

    return results["C++"], results["Java"], results["Rust"]


# Benchmark execution and visualization
def execute_and_benchmark(python_code, cpp_code, java_code, rust_code):
    """
    Execute all code versions in Docker and create performance comparison
    
    Returns:
        tuple: (matplotlib_figure, results_markdown)
    """
    # Run benchmark in Docker
    print("[Benchmark] Starting execution...")
    results = run_benchmark(python_code, cpp_code, java_code, rust_code)
    
    # DEBUG: Print what we received
    print(f"[DEBUG] Results received: {results}")
    print(f"[DEBUG] Results type: {type(results)}")
    print(f"[DEBUG] Results keys: {results.keys() if isinstance(results, dict) else 'Not a dict'}")
    
    # Check for errors
    if "error" in results and not any(k in results for k in ['python', 'cpp', 'java', 'rust']):
        error_msg = f"### ❌ Benchmark Error\n\n```\n{results['error']}\n```"
        return None, error_msg
    
    # Extract execution times and prepare data
    languages = []
    times = []
    colors = []
    statuses = []
    outputs = []
    
    lang_config = {
        'python': {'name': 'Python', 'color': '#3776ab'},
        'cpp': {'name': 'C++', 'color': '#00599C'},
        'java': {'name': 'Java', 'color': '#007396'},
        'rust': {'name': 'Rust', 'color': '#f74c00'}
    }
    
    for lang_key, config in lang_config.items():
        if lang_key in results:
            result = results[lang_key]
            languages.append(config['name'])
            
            if result.get('success', False):
                exec_time = result.get('execution_time', 0)
                times.append(exec_time * 1000)  # Convert to milliseconds
                colors.append(config['color'])
                statuses.append('✓')
                outputs.append(result.get('output', '')[:100])  # First 100 chars
            else:
                times.append(0)
                colors.append('#666666')
                statuses.append('✗')
                outputs.append(result.get('error', 'Unknown error')[:100])
    
    # Create visualization
    if any(t > 0 for t in times):
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bar chart
        bars = ax.barh(languages, times, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        
        # Styling
        ax.set_xlabel('Execution Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Performance Comparison', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for i, (bar, time, status) in enumerate(zip(bars, times, statuses)):
            if time > 0:
                label = f'{status} {time:.2f}ms'
                ax.text(time, bar.get_y() + bar.get_height()/2, 
                       f'  {label}', va='center', fontsize=10, fontweight='bold')
        
        # Set background
        ax.set_facecolor('#f8f9fa')
        fig.patch.set_facecolor('white')
        
        plt.tight_layout()
    else:
        fig = None
    
    # Generate results summary
    markdown_lines = ["### 📊 Benchmark Results\n"]
    
    # Find fastest successful execution
    successful_times = [(lang, time) for lang, time, status in zip(languages, times, statuses) 
                        if status == '✓' and time > 0]
    
    if successful_times:
        fastest_lang, fastest_time = min(successful_times, key=lambda x: x[1])
        python_time = next((time for lang, time in zip(languages, times) if lang == 'Python'), None)
        
        markdown_lines.append(f"**🏆 Fastest:** {fastest_lang} ({fastest_time:.2f}ms)\n")
        
        if python_time and python_time > 0 and fastest_time > 0:
            speedup = python_time / fastest_time
            markdown_lines.append(f"**⚡ Speedup:** {speedup:.1f}x faster than Python\n")
        
        markdown_lines.append("\n---\n")
        markdown_lines.append("#### Detailed Results:\n")
        
        for lang, time, status in zip(languages, times, statuses):
            if status == '✓' and time > 0:
                if python_time and python_time > 0 and time > 0:
                    relative_speed = python_time / time
                    markdown_lines.append(
                        f"- **{lang}**: {time:.2f}ms ({relative_speed:.1f}x vs Python) {status}\n"
                    )
                else:
                    markdown_lines.append(f"- **{lang}**: {time:.2f}ms {status}\n")
            else:
                markdown_lines.append(f"- **{lang}**: Failed {status}\n")
    else:
        markdown_lines.append("**❌ No successful executions**\n\n")
        markdown_lines.append("All languages failed to execute. Check the code for errors.\n")
    
    # Add individual outputs/errors
    markdown_lines.append("\n---\n")
    markdown_lines.append("#### Execution Details:\n")
    
    for lang_key, config in lang_config.items():
        if lang_key in results:
            result = results[lang_key]
            markdown_lines.append(f"\n**{config['name']}:**\n")
            
            if result.get('success', False):
                output = result.get('output', 'No output')
                markdown_lines.append(f"```\n{output[:200]}\n```\n")
            else:
                error = result.get('error', 'Unknown error')
                markdown_lines.append(f"```\n❌ {error[:200]}\n```\n")
    
    return fig, ''.join(markdown_lines)


## Gradio UI
def load_python_file(file):
    if file is None:
        return ""
    
    with open(file.name, 'r') as f:
        return f.read()
    
with gr.Blocks(title="Code Porter - Python to Native") as app:
    
    # Header
    gr.HTML("""
        <div class="app-header">
            <h1>Code Porter</h1>
            <p>Transform Python code into high-performance C++, Java, and Rust</p>
        </div>
    """)
    
    with gr.Row():
        # Left panel - Python source
        with gr.Column(scale=1):
            gr.HTML('<span class="lang-label" style="background: #3776ab; color: white;">Python (Original)</span>')
            
            python_code = gr.Code(
                value=DEFAULT_PYTHON,
                language="python",
                label="Python Source Code",
                lines=25,
                elem_classes=["code-editor"]
            )
            
            with gr.Row():
                file_upload = gr.File(
                    label="Upload .py",
                    file_types=[".py"],
                    file_count="single",
                    elem_classes=["file-upload"]
                )
                model_dropdown = gr.Dropdown(
                    choices=models,
                    value="gpt-5",
                    label="Model",
                    elem_classes=["model-dropdown"]
                )
            
            with gr.Row():
                port_btn = gr.Button(
                    "Port Code",
                    variant="primary",
                    elem_classes=["primary-btn"],
                    size="lg"
                )
                execute_btn = gr.Button(
                    "Execute All & Evaluate",
                    variant="secondary",
                    elem_classes=["secondary-btn"],
                    size="lg"
                )
        
        # Right panel - Ported code with tabs
        with gr.Column(scale=1):
            gr.HTML('<span style="color: #b0d0b0; font-weight: 600; font-size: 14px;">Ported Code</span>')
            
            with gr.Tabs() as code_tabs:
                with gr.Tab("C++", id="cpp"):
                    cpp_code = gr.Code(
                        value="// C++ code will appear here after porting",
                        language="cpp",
                        label="",
                        lines=22,
                        elem_classes=["code-editor"],
                        show_label=False
                    )
                
                with gr.Tab("Java", id="java"):
                    java_code = gr.Code(
                        value="// Java code will appear here after porting",
                        language="c",
                        label="",
                        lines=22,
                        elem_classes=["code-editor"],
                        show_label=False
                    )
                
                with gr.Tab("Rust", id="rust"):
                    rust_code = gr.Code(
                        value="// Rust code will appear here after porting",
                        language="c",
                        label="",
                        lines=22,
                        elem_classes=["code-editor"],
                        show_label=False
                    )
    
    # Performance comparison section
    gr.HTML("""
        <div class="section-header">
            <h3>Performance Comparison</h3>
        </div>
    """)
    
    with gr.Row():
        with gr.Column():
            # Performance graph
            performance_plot = gr.Plot(
                label="Execution Time Comparison",
                elem_classes=["graph-placeholder"]
            )
        
        with gr.Column():
            # Results summary
            results_summary = gr.Markdown(
                """
                ### Results Summary
                
                Run **Execute All & Evaluate** to see:
                - Execution times for each language
                - Performance ranking
                - Speedup compared to Python
                
                *Results will appear here after execution...*
                """,
                elem_classes=["result-panel"]
            )
    
    # Event handlers
    file_upload.change(
        fn=load_python_file,
        inputs=[file_upload],
        outputs=[python_code]
    )
    
    def port_with_status(python_code, model):
        """Wrapper that returns ported code."""
        cpp, java, rust = port_all_languages(python_code, model)
        return cpp, java, rust
    
    port_btn.click(
        fn=lambda: (gr.update(interactive=False), gr.update(interactive=False)),
        inputs=[],
        outputs=[port_btn, execute_btn]
    ).then(
        fn=port_with_status,
        inputs=[python_code, model_dropdown],
        outputs=[cpp_code, java_code, rust_code]
    ).then(
        fn=lambda: (gr.update(interactive=True), gr.update(interactive=True)),
        inputs=[],
        outputs=[port_btn, execute_btn]
    )
    
    # Execute and benchmark button
    execute_btn.click(
        fn=lambda: (gr.update(interactive=False), gr.update(interactive=False)),
        inputs=[],
        outputs=[port_btn, execute_btn]
    ).then(
        fn=execute_and_benchmark,
        inputs=[python_code, cpp_code, java_code, rust_code],
        outputs=[performance_plot, results_summary]
    ).then(
        fn=lambda: (gr.update(interactive=True), gr.update(interactive=True)),
        inputs=[],
        outputs=[port_btn, execute_btn]
    )


## main == __init__
if __name__ == "__main__":
    import signal
    import atexit
    
    def cleanup():
        """Clean up resources on exit."""
        print("\n[Code Porter] Shutting down...")
        try:
            # Cleanup Docker (optional - image persists for faster restarts)
            # Uncomment to remove Docker image on exit:
            # cleanup_manager()

            gr.close_all()
            print("[Code Porter] Server closed successfully.")
        except Exception as e:
            print(f"[Code Porter] Cleanup error: {e}")
    
    def signal_handler(signum, frame):
        """Handle interrupt signals."""
        cleanup()
        exit(0)
    
    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill command
    
    try:
        print("[Code Porter] Starting server on http://localhost:7860")
        print("[Code Porter] Initializing Docker environment...")

        get_manager()
        print("[Code Porter] Docker ready!")

        app.launch(
            server_port=7860,
            css=CUSTOM_CSS,
            inbrowser=True
        )
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print(f"[Code Porter] Error: {e}")
        cleanup()
