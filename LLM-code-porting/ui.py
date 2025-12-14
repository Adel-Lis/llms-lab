"""
Gradio UI - Web interface for Code Porter
"""

import gradio as gr

from config import MODELS
from llm_porter import port_all_languages
from benchmark_runner import execute_and_benchmark
from styles import DEFAULT_PYTHON


def load_python_file(file):
    if file is None:
        return ""
    
    with open(file.name, 'r') as f:
        return f.read()
    
def create_interface():
    with gr.Blocks(title="Code Porter - Python to Native") as app:
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
                        choices=MODELS,
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
        
    return app