import os
import re
import json
import argparse
import sys
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Any
import git
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


# Detection Rules
PATTERNS = {
    'aws_access_key': r'AKIA[0-9A-Z]{16}',
    'aws_secret_key': r'(?i)aws.{0,20}?(?:secret|access.?key|password).{0,20}?[\'"][0-9a-zA-Z/+=]{40}[\'"]',
    'google_api_key': r'AIza[0-9A-Za-z\-_]{35}',
    'openai_api_key': r'sk-[a-zA-Z0-9]{20,}',
    'anthropic_api_key': r'sk-ant-[a-zA-Z0-9\-_]{95,}',
    'github_token': r'ghp_[A-Za-z0-9]{36}',
    'github_oauth': r'gho_[A-Za-z0-9]{36}',
    'slack_token': r'xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24,}',
    'slack_webhook': r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+',
    'stripe_api_key': r'sk_live_[0-9a-zA-Z]{24,}',
    'password_assignment': r'(?i)password\s*=\s*[\'"][^\'"]{4,}[\'"]',
    'api_key_assignment': r'(?i)(?:api[_-]?key|apikey)\s*=\s*[\'"][^\'"]{8,}[\'"]',
    'secret_assignment': r'(?i)secret\s*=\s*[\'"][^\'"]{8,}[\'"]',
    'token_assignment': r'(?i)token\s*=\s*[\'"][^\'"]{8,}[\'"]',
    'private_key': r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
    'jwt_token': r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
    'generic_secret': r'(?i)(?:secret|password|passwd|pwd|token|api[_-]?key)[\"\']\s*:\s*[\"\'"][^\'"]{8,}[\"\'"]',
    'connection_string': r'(?i)(?:mongodb|mysql|postgres|redis)://[^\s]{10,}',
    'bearer_token': r'(?i)bearer\s+[a-zA-Z0-9\-_\.]{20,}',
}

SECRET_KEYWORDS = [
    'password', 'passwd', 'pwd', 'secret', 'api_key', 'apikey', 'access_key',
    'secret_key', 'token', 'auth', 'credential', 'private_key', 'bearer'
]


# Repository Handling
def is_git_url(path: str) -> bool:
    """Check if the path is a Git URL"""
    return bool(re.match(r'^(https?://|git@|ssh://)', path) or path.endswith('.git'))


def clone_repository(url: str) -> str:
    """Clone a Git repository from URL to temporary directory"""
    print(f"Cloning repository from: {url}")
    
    temp_dir = tempfile.mkdtemp(prefix='git_secrets_scanner_')
    
    try:
        git.Repo.clone_from(url, temp_dir, depth=100)
        print(f"Repository cloned to: {temp_dir}")
        return temp_dir
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"Error: Failed to clone repository: {str(e)}")
        sys.exit(1)


# Helper Functions for Scanning
def scan_line(line: str, line_num: int) -> List[Dict[str, Any]]:
    """Scan a single line for secrets"""
    findings = []
    
    if len(line.strip()) < 5:
        return findings
    
    # Check each pattern
    for pattern_name, pattern in PATTERNS.items():
        matches = re.finditer(pattern, line)
        for match in matches:
            matched_text = match.group(0)
            
            secret_value = matched_text
            quote_match = re.search(r'[\'"]([^\'"]+)[\'"]', matched_text)
            if quote_match:
                secret_value = quote_match.group(1)
            
            findings.append({
                'type': pattern_name,
                'matched_text': secret_value[:100],  # Limit length
                'full_line': line.strip()[:200],
                'line_number': line_num
            })
    
    # Check for high entropy strings near keywords
    for keyword in SECRET_KEYWORDS:
        if keyword in line.lower():
            potential = re.findall(r'["\']([^"\']{12,80})["\']', line)
            potential += re.findall(r'=\s*([A-Za-z0-9+/=_-]{16,80})(?:\s|$|,|;)', line)
            
            for secret in potential:
                if has_high_entropy(secret):
                    findings.append({
                        'type': 'high_entropy_near_keyword',
                        'matched_text': secret[:100],
                        'full_line': line.strip()[:200],
                        'line_number': line_num,
                        'keyword': keyword
                    })
                    break
    
    return findings


def has_high_entropy(s: str) -> bool:
    """Check if string has high entropy (likely random)"""
    if len(s) < 12:
        return False
    
    if len(set(s)) < len(s) * 0.4:
        return False
    
    has_upper = any(c.isupper() for c in s)
    has_lower = any(c.islower() for c in s)
    has_digit = any(c.isdigit() for c in s)
    
    # High entropy if it has at least 2 types and good character diversity
    char_types = sum([has_upper, has_lower, has_digit])
    return char_types >= 2 and len(set(s)) >= 8


def is_false_positive(text: str, line: str) -> bool:
    """Basic false positive check"""
    text_lower = text.lower()
    line_lower = line.lower()
    
    # Common false positive patterns
    fp_patterns = [
        'example', 'sample', 'test', 'dummy', 'fake', 'placeholder',
        'your_api_key', 'insert_', 'replace_', 'todo', 'fixme',
        'xxx', '***', 'redacted', '<secret>', '[secret]', 'changeme',
        'your_password', 'my_password', '12345', 'qwerty', 'password123'
    ]
    
    for pattern in fp_patterns:
        if pattern in text_lower or pattern in line_lower:
            return True
    
    if len(set(text)) <= 2:
        return True
    
    return False


# Git Analysis
def analyze_repository(repo_path: str, n_commits: int) -> List[Dict[str, Any]]:
    """Analyze last N commits in a Git repository""" 
    try:
        repo = git.Repo(repo_path)
    except Exception as e:
        print(f"Error: Failed to open repository: {str(e)}")
        sys.exit(1)
    
    print(f"Scanning last {n_commits} commits...\n")
    
    all_findings = []
    commits = list(repo.iter_commits('HEAD', max_count=n_commits))
    
    if not commits:
        print("No commits found in repository")
        return []
    
    for idx, commit in enumerate(commits):
        print(f"Commit {idx + 1}/{len(commits)}: {commit.hexsha[:8]} - {commit.message.split()[0] if commit.message else 'No message'}...")
        
        commit_findings = []
        
        # Scan commit message
        msg_findings = scan_line(commit.message, 0)
        for finding in msg_findings:
            finding['commit_hash'] = commit.hexsha
            finding['commit_message'] = commit.message[:100]
            finding['file_path'] = '[COMMIT_MESSAGE]'
            commit_findings.append(finding)
        
        # Scan diffs
        if commit.parents:
            parent = commit.parents[0]
            
            try:
                diffs = parent.diff(commit, create_patch=True)
                
                for diff in diffs:
                    file_path = diff.b_path or diff.a_path or 'unknown'
                    
                    if file_path and any(file_path.endswith(ext) for ext in ['.png', '.jpg', '.gif', '.pdf', '.zip', '.jar']):
                        continue
                    
                    if diff.diff:
                        try:
                            diff_text = diff.diff.decode('utf-8', errors='ignore')
                        except:
                            continue
                        
                        lines = diff_text.split('\n')
                        current_line_num = 0
                        
                        for line in lines:
                            if line.startswith('@@'):
                                match = re.search(r'\+(\d+)', line)
                                if match:
                                    current_line_num = int(match.group(1))
                                continue
                            
                            if line.startswith('+') and not line.startswith('+++'):
                                actual_line = line[1:] 
                                
                                line_findings = scan_line(actual_line, current_line_num)
                                
                                for finding in line_findings:
                                    finding['commit_hash'] = commit.hexsha
                                    finding['commit_message'] = commit.message[:100]
                                    finding['file_path'] = file_path
                                    commit_findings.append(finding)
                                
                                current_line_num += 1
                            elif not line.startswith('-'):
                                current_line_num += 1
                
            except Exception as e:
                print(f"  Warning: Error processing commit diffs: {str(e)}")
        
        if commit_findings:
            print(f"  Found {len(commit_findings)} potential secrets")
            all_findings.extend(commit_findings)
        else:
            print(f"  No secrets found")
    
    print(f"\nTotal potential secrets found (before validation): {len(all_findings)}")
    
    filtered = []
    for finding in all_findings:
        if not is_false_positive(finding['matched_text'], finding['full_line']):
            filtered.append(finding)
    
    print(f"After basic filtering: {len(filtered)} findings")
    
    # LLM validation
    if filtered:
        validated = validate_with_llm(filtered)
        return validated
    
    return filtered


# ============================================================================
# LLM VALIDATION
# ============================================================================

def validate_with_llm(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Use OpenAI to validate findings"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Skipping LLM validation.\n")
        for finding in findings:
            finding['confidence'] = 'medium'
            finding['rationale'] = 'No LLM validation performed'
            finding['llm_validated'] = False
        return findings
    
    print(f"\nValidating {len(findings)} findings with LLM...")
    
    client = OpenAI(api_key=api_key)
    validated = []
    
    # Process in batches
    batch_size = 10
    for i in range(0, len(findings), batch_size):
        batch = findings[i:i+batch_size]
        
        findings_text = ""
        for idx, f in enumerate(batch):
            findings_text += f"\n{idx+1}. Type: {f['type']}\n"
            findings_text += f"   Value: {f['matched_text']}\n"
            findings_text += f"   Line: {f['full_line']}\n"
            findings_text += f"   File: {f['file_path']}\n"
        
        prompt = f"""You are a security expert that analyzes these potential secrets found in a Git repository.

                    For each finding, determine:
                    1. Is it a REAL secret that should be flagged? (yes/no)
                    2. Confidence: high/medium/low
                    3. Brief reason (one sentence)

                    MARK AS FALSE POSITIVE (say "no"):
                    - Test data, examples, documentation
                    - Placeholder values like "your_api_key_here"
                    - Already found values

                    MARK AS "YES":
                    - Actual API keys, tokens, passwords
                    - Real credentials that could work
                    - Private keys
                    - Connection strings with real hosts

                    Findings:
                    {findings_text}

                    Respond ONLY with this JSON array (no other text). Example:
                    [
                    {{"id": 1, "is_real": "yes", "confidence": "high", "reason": "Actual OpenAI API key with valid format"}},
                    {{"id": 2, "is_real": "no", "confidence": "low", "reason": "Example placeholder value"}},
                    ...
                    ]
                """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a security expert looking for security vulnerabilities. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                results = json.loads(json_match.group(0))
                
                for idx, finding in enumerate(batch):
                    if idx < len(results):
                        r = results[idx]
                        
                        if r.get('is_real', 'no').lower() == 'yes':
                            finding['confidence'] = r.get('confidence', 'medium')
                            finding['rationale'] = r.get('reason', 'Flagged by LLM')
                            finding['llm_validated'] = True
                            validated.append(finding)
            else:
                for finding in batch:
                    finding['confidence'] = 'low'
                    finding['rationale'] = 'LLM validation failed'
                    finding['llm_validated'] = False
                    validated.append(finding)
        
        except Exception as e:
            print(f"  LLM validation error: {str(e)}")
            for finding in batch:
                finding['confidence'] = 'medium'
                finding['rationale'] = f'LLM error: {str(e)}'
                finding['llm_validated'] = False
                validated.append(finding)
    
    print(f"After LLM validation: {len(validated)} confirmed findings\n")
    return validated


# ============================================================================
# REPORT
# ============================================================================

def generate_report(findings: List[Dict[str, Any]], output_file: str):
    """Generate JSON report"""
    
    report = {
        'scan_timestamp': datetime.now().isoformat(),
        'total_findings': len(findings),
        'findings': findings,
        'summary': {
            'high_confidence': len([f for f in findings if f.get('confidence') == 'high']),
            'medium_confidence': len([f for f in findings if f.get('confidence') == 'medium']),
            'low_confidence': len([f for f in findings if f.get('confidence') == 'low']),
            'by_type': {}
        }
    }
    
    for f in findings:
        ftype = f.get('type', 'unknown')
        report['summary']['by_type'][ftype] = report['summary']['by_type'].get(ftype, 0) + 1
    
    with open(output_file, 'w') as file:
        json.dump(report, file, indent=2)
    
    print(f"\nReport saved: {output_file}")


# CLI
def main():
    parser = argparse.ArgumentParser(description='Git Secrets Scanner')
    parser.add_argument('--repo', type=str, default='.', help='Repository path or GitHub URL')
    parser.add_argument('--n', type=int, default=10, help='Number of commits to scan')
    parser.add_argument('--out', type=str, default='secrets_report.json', help='Output file')
    
    args = parser.parse_args()
    
    print("== Git Secrets Scanner ==\n")
    
    temp_dir = None
    repo_path = args.repo
    
    if is_git_url(args.repo):
        temp_dir = clone_repository(args.repo)
        repo_path = temp_dir
    
    try:
        findings = analyze_repository(repo_path, args.n)
        generate_report(findings, args.out)
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()