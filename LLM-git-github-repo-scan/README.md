# Git Secrets Scanner

**Author:** Adel Lis  
**Contact:** adel.lis.work@gmail.com
> This project was developed as my solution to the requested task for the JetBrains Internship - LLM-Powered Automation for Cyber Security job interview.

---

## Project Overview

In this project I implemented an automated secrets detection tool that scans Git repositories (through remote repo link or local path) for exposed sensitive information such as API keys, passwords, tokens, and credentials. The scanner analyzes commit history and uses pattern matching, entropy analysis, and LLM validation to identify potential security leaks.

The scanner works by examining the last `N` commits in the given repository, it extracts diffs to see what was added or modified, and runs multiple detection strategies on each line of code. I used regex-based pattern matching to catch known secret formats like AWS keys, GitHub tokens, OpenAI API keys, Stripe keys, private keys, and others. In addition I also looks for high-entropy strings near security-related keywords because I want to also catch custom or unknown secret formats that don't match my predefined patterns.

### GitHub Commits and Diffs Extraction

The scanner uses `GitPython` to interact with repositories. It can work with both local repository paths and remote GitHub URLs. When given a URL, the script clones the repository to a temporary directory and performs the scan there (when the program ends, the temporary folder is deleted). The tool iterates through the last `N` commits and for each commit, it extracts the diff to see what lines were added. The scanner parses the unified diff format, it tracks line numbers and identifies added lines (those starting with '+'), then runs the detection algorithms only on new content. I also decided to scan commit messages themselves.

### Entropy Calculation

For detecting unknown or custom secret formats I implemented an entropy-based detection system. When a line contains security-related keywords like "password", "api_key", "token", "secret", or "credential", the scanner extracts quoted strings or values after the equals signs and calculates their entropy. The entropy check looks at character diversity and type distribution. I have decided that a string is flagged as high-entropy if it has at least 40% unique characters, contains at least 2 different character types (uppercase, lowercase, digits), and has at least 8 unique characters overall. Through this decision I aim to catch randomly-generated secrets that don't match known patterns.

### LLM Validation

After the initial pattern and entropy-based detection, all findings are sent to an LLM for validation to reduce false positives. I chose the **OpenAI API** (specifically the `gpt-4o-mini` model) API step. The *system promps* given to the LLM instructs it to be a security expert that reviews each potential finding and determines whether it's a real secret or a false positive. The *user prompt* tells the LLM to mark as false positives: test data, placeholder values (like "your_api_key_here"), and already found values. Real secrets are identified as actual API keys with valid formats, credentials that could work in production, private keys, and connection strings with real hosts. The LLM responds in JSON and for each finiding it sets a confidence level (high/medium/low) and a brief reason for each decision.

**Important:** To use this project, you **MUST** create a `.env` file in the project root with your OpenAI API key. Without this key, the scanner will still work but will skip the LLM validation step and mark all findings with medium confidence. The `.env` file should look like this:

```
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
```

You can obtain an API key from https://platform.openai.com/api-keys

---

## Setup and Running the Project

I have used Anaconda as my enviornment management to build this project. You can set up this project using Anaconda or a .venv, here I described the set up process:

### Option 1: Setup with Anaconda

1. **Create a new Conda environment:**
```bash
conda create -n secrets-scanner python=3.10
```

2. **Activate the environment:**
```bash
conda activate secrets-scanner
```

3. **Install required packages:**
```bash
pip install GitPython openai python-dotenv
```

### Option 2: Setup with pip

1. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install required packages:**
```bash
pip install GitPython openai python-dotenv
```

### Running the Scanner

The basic command structure is:

```bash
python scan.py --repo <path|url> --n <commits> --out <output_file>
```

**Parameters:**
- `--repo`: Repository path (local directory) or GitHub URL (required, defaults to current directory)
- `--n`: Number of recent commits to scan (optional, default is 10)
- `--out`: Output JSON report filename (optional, default file name is `secrets_report.json` and will be created in the same directory as the python script)

### Example: Test Repository Scan

Here I want to show you how this project work with a quick and nice example. I created a test repository specifically for demonstrating the capabilities of my python implementation. The 'fake' repo has intentionally fake secrets: https://github.com/Adel13Lis/test_repo

Running the scanner on this test repository:

```bash
python scan.py --repo https://github.com/Adel13Lis/test_repo --n 8
```

This command scans the last 8 commits of the test repository and produces a report like this:

```json
{
  "scan_timestamp": "2025-11-12T02:17:33.869607",
  "total_findings": 8,
  "findings": [
    {
      "type": "api_key_assignment",
      "matched_text": "sk-live-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
      "full_line": "API_KEY = \"sk-live-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6\"",
      "line_number": 2,
      "commit_hash": "a0601e461e60659ec33655646e156020e71175f8",
      "commit_message": "Create .env file with configuration variables",
      "file_path": ".env",
      "confidence": "high",
      "rationale": "Actual API key with valid format.",
      "llm_validated": true
    },
    {
      "type": "aws_access_key",
      "matched_text": "AKIAIOSFODNN7EXAMPLE",
      "full_line": "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE",
      "line_number": 5,
      "commit_hash": "b3f5e8c9d2a1f4e6b7c8d9e0f1a2b3c4d5e6f7a8",
      "commit_message": "Add AWS credentials to config",
      "file_path": "config.py",
      "confidence": "high",
      "rationale": "Valid AWS access key format.",
      "llm_validated": true
    },
    ...
  ],
  "summary": {
    "high_confidence": 8,
    "medium_confidence": 0,
    "low_confidence": 0,
    "by_type": {
      "api_key_assignment": 1,
      "high_entropy_near_keyword": 1,
      "aws_access_key": 1,
      "github_token": 1,
      "password_assignment": 1,
      "openai_api_key": 1,
      "connection_string": 1,
      "private_key": 1
    }
  }
}
```

The report shows that the scanner successfully identified 8 different types of secrets across multiple commits, with each finding including the commit hash, file path, line number, and confidence level determined by the LLM validator.