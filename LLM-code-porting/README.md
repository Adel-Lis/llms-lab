# Code Porter

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-Required-2496ED?style=flat&logo=docker&logoColor=white) ![Gradio 4+](https://img.shields.io/badge/gradio-4%2B-orange?logo=gradio&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-green?style=flat)

**LLM-Powered Python to Native Code Converter with Performance Benchmarking**

---

## What is Code Porter?

Code Porter is a small web application that uses Large Language Models to automatically translate Python code into C++, Java, and Rust. After translation, it compiles and executes all versions in isolated Docker containers to measure and compare their performance.

The core idea is simple: Python is great for development speed, but what if you need execution speed? Code Porter answers the question "How much faster could my code be?" by actually running the translated versions and showing you real performance numbers.

## Why This Project?

**The Performance Problem**

Python is fantastic for rapid prototyping and development, but it can be painfully slow for computationally intensive tasks. When you need that critical algorithm to run faster, you're faced with learning C++, Rust, or Java from scratch, then manually rewriting your logic. This is time-consuming and error-prone.

**The AI Solution**

Modern Language Models can translate code between programming languages with impressive accuracy. Code Porter answers with a solution to automatically generate optimized implementations in three compiled languages.

**Comparing AI Models**

This project also serves as a testing ground for evaluating both proprietary LLMs (GPT-5, Claude Sonnet, Grok) and open-source alternatives (running locally via Ollama). You can directly compare how well different models handle code translation, optimization, and edge cases. This helps answer which AI tools are best for code generation tasks.

**Real-World Applications**

Whether you're optimizing a production bottleneck, researching algorithm performance, or just learning how different languages handle the same problem, Code Porter makes the process interactive and visual. Instead of guessing at performance gains, you get concrete measurements showing that your algorithm runs 50x faster in Rust or 94x faster in Java.

---

## Quick Start

### Prerequisites

You'll need Python 3.7 or higher and Docker installed on your system. For detailed Docker installation instructions covering Windows, macOS, and all major Linux distributions, see the [Docker Setup Guide](DOCKER_SETUP.md).

You'll also need at least one API key from OpenAI, Anthropic, or Grok. Alternatively, you can use free open-source models through Ollama running locally on your machine.

### Installation

First, clone the repository:

```bash
git clone [https://github.com/yourusername/code-porter.git](https://github.com/Adel-Lis/llms-lab.git)
cd llms-lab/LLM-code-porting/
```

**Option 1: Using uv (fastest)**

```bash
# Install uv if you haven't already
pip install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

**Option 2: Using Anaconda**

```bash
# Create new environment
conda create -n codeporter python=3.10
conda activate codeporter

# Install dependencies
pip install -r requirements.txt
```

**Option 3: Using standard venv**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root with at least one API key:

```env
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GROK_API_KEY=xai-your-key-here
```

To use free open-source models instead, install Ollama from https://ollama.com and pull the models:

```bash
ollama pull minimax-m2:cloud
ollama pull kimi-k2-thinking:cloud
ollama pull deepseek-v3.2:cloud
ollama pull gpt-oss:120b:cloud
```

### Running the App

Start the application:

```bash
python main.py
```

On first run, Docker will build the benchmark image (takes 2-5 minutes). After that, the app opens automatically at http://localhost:7860. Subsequent runs start instantly.

---

## How to Use

The interface is straightforward. On the left side, you'll find a Python code editor. You can either type code directly or upload a `.py` file. The default example code is already loaded to get you started quickly.

Select which AI model you want to use from the dropdown menu. The closed-source models (GPT-5, Claude, Grok) require API keys and generally produce higher quality code. The open-source models run locally through Ollama and are completely free to use.

Click the "Port Code" button to start the translation. The AI will generate `C++`, `Java`, and `Rust` versions of your `Python` code in parallel. The results appear in separate tabs on the right side, and you can review, edit, or download them before running and executing benchmarks.

When you're ready to benchmark, click "Execute All & Evaluate". This sends all four code versions into a Docker container where they're compiled and executed. The system measures execution time with nanosecond precision and displays the results in two ways.

First, you'll see a performance chart using a logarithmic scale so all bars are visible even when there's a 100x speed difference. A red curve overlays the bars showing the exponential performance improvement. Second, you'll get a detailed ranking showing which language was fastest and by how much. For example, you might see that Rust executed in 2.4ms while Python took 123ms, making Rust 51 times faster.

You can iterate freely by modifying the generated code, trying different models, or testing new Python code. Each benchmark run is isolated and doesn't affect previous results.

---

## Supported Models

**Closed-Source Models** require API keys but generally produce better code quality. These include:

- `GPT-5` from OpenAI,
- `Claude Sonnet 4.5` from Anthropic,
- `Grok-4` from xAI.

They excel at understanding complex logic, handling edge cases, and generating optimized implementations.

**Open-Source Models** run locally via Ollama and are completely free. These include:

- `GPT-OSS (120B parameters)`,
- `MiniMax M2`,
- `DeepSeek V3.2`,
- `Kimi K2 Thinking`.

I found interesting to test these powerful open source models because these performed quite well in the [ArtificialAnalysis.ai](https://artificialanalysis.ai/) benchmarks. Also, I used all these open source models, by pulling their cloud versions and have no model physically installed on my device.

---

## License

MIT License - see LICENSE file for details.

---

## Acknowledgments

Anthropic model Optus-4.5 was used in this application to help me build the UX/UI, Docker Setup, README documentations and file structure correction.
