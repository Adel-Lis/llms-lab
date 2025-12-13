"""
Docker Environment Setup and Management for Code Benchmarking
Handles Docker image building, code execution, and performance measurement
"""

import docker
import json
import os
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

class DockerBenchmarkManager:
    """Manages Docker operations for multi-language code benchmarking"""
    
    def __init__(self, dockerfile_path=".", image_name="code-porter-benchmark:latest"):
        """
        Initialize Docker manager
        
        Args:
            dockerfile_path: Path to directory containing Dockerfile
            image_name: Name for the Docker image
        """
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
        except Exception as e:
            raise RuntimeError(
                f"Docker connection failed: {e}\n"
                "Make sure Docker is installed and running."
            )
        
        self.dockerfile_path = dockerfile_path
        self.image_name = image_name
        self.image_built = False
        
        # System info from the Docker container
        self.system_info = "Ubuntu 22.04 x86_64 (Docker)"
        
        # Compile commands for each language
        self.compile_commands = {
            "cpp": "g++ -O3 -std=c++17 -march=native code.cpp -o cpp_program",
            "java": "javac Main.java",
            "rust": "rustc -C opt-level=3 -C target-cpu=native code.rs -o rust_program"
        }
    
    def get_system_info(self) -> str:
        """Get system information for code generation prompts"""
        return self.system_info
    
    def get_compile_command(self, language: str) -> str:
        """Get compile command for a specific language"""
        return self.compile_commands.get(language.lower(), "")
    
    def build_image(self) -> bool:
        """Build the Docker image with all compilers"""
        try:
            print(f"[Docker] Building image '{self.image_name}'...")
            print("[Docker] This may take 2-5 minutes on first run...")
            
            # Build the image
            image, build_logs = self.client.images.build(
                path=self.dockerfile_path,
                tag=self.image_name,
                rm=True,
                forcerm=True,
                pull=True  # Pull latest base image
            )
            
            # Print build progress (only errors and important messages)
            for log in build_logs:
                if 'stream' in log:
                    msg = log['stream'].strip()
                    if msg and ('Step' in msg or 'error' in msg.lower()):
                        print(f"[Docker] {msg}")
                elif 'error' in log:
                    print(f"[Docker Error] {log['error']}")
            
            self.image_built = True
            print(f"[Docker] ✓ Image '{self.image_name}' built successfully!")
            return True
            
        except docker.errors.BuildError as e:
            print(f"[Docker Error] Build failed: {e}")
            for log in e.build_log:
                if 'stream' in log:
                    print(log['stream'].strip())
            return False
        except Exception as e:
            print(f"[Docker Error] {e}")
            return False
    
    def ensure_image_exists(self) -> bool:
        """Check if image exists, build if not"""
        try:
            self.client.images.get(self.image_name)
            self.image_built = True
            print(f"[Docker] ✓ Image '{self.image_name}' already exists (using cached)")
            return True
        except docker.errors.ImageNotFound:
            print(f"[Docker] Image not found. Building...")
            return self.build_image()
        except Exception as e:
            print(f"[Docker Error] {e}")
            return False
    
    def run_benchmark(
        self, 
        python_code: str, 
        cpp_code: str, 
        java_code: str, 
        rust_code: str
    ) -> Dict:
        """
        Run benchmark on all code files
        
        Args:
            python_code: Python source code
            cpp_code: C++ source code
            java_code: Java source code
            rust_code: Rust source code
            
        Returns:
            dict: Benchmark results with execution times and outputs
        """
        # Ensure image exists
        if not self.image_built:
            if not self.ensure_image_exists():
                return {
                    "error": "Failed to build Docker image",
                    "python": {"success": False, "error": "Docker setup failed"},
                    "cpp": {"success": False, "error": "Docker setup failed"},
                    "java": {"success": False, "error": "Docker setup failed"},
                    "rust": {"success": False, "error": "Docker setup failed"}
                }
        
        # Create temporary directory for code files
        temp_dir = tempfile.mkdtemp(prefix="code_porter_")
        
        try:
            # Write code files to temp directory
            files_written = {}
            
            if python_code and python_code.strip():
                python_path = os.path.join(temp_dir, "code.py")
                with open(python_path, 'w', encoding='utf-8') as f:
                    f.write(python_code)
                files_written['python'] = True
            
            if cpp_code and cpp_code.strip() and not cpp_code.startswith("//"):
                cpp_path = os.path.join(temp_dir, "code.cpp")
                with open(cpp_path, 'w', encoding='utf-8') as f:
                    f.write(cpp_code)
                files_written['cpp'] = True
            
            if java_code and java_code.strip() and not java_code.startswith("//"):
                java_path = os.path.join(temp_dir, "Main.java")
                with open(java_path, 'w', encoding='utf-8') as f:
                    f.write(java_code)
                files_written['java'] = True
            
            if rust_code and rust_code.strip() and not rust_code.startswith("//"):
                rust_path = os.path.join(temp_dir, "code.rs")
                with open(rust_path, 'w', encoding='utf-8') as f:
                    f.write(rust_code)
                files_written['rust'] = True
            
            print(f"[Docker] Running benchmark for: {', '.join(files_written.keys())}")
            
            # Run container with volume mount (DON'T auto-remove yet)
            container = self.client.containers.run(
                self.image_name,
                command="python3 /app/benchmark.py",
                volumes={temp_dir: {'bind': '/app/code', 'mode': 'rw'}},
                detach=True,
                remove=False,  # Don't auto-remove - we'll do it manually after getting logs
                mem_limit="1g",  # Limit memory to 1GB
                cpu_period=100000,
                cpu_quota=100000,  # Limit to 1 CPU core
                network_mode="none"  # No network access for security
            )
            
            # Wait for container to finish (with timeout)
            try:
                result = container.wait(timeout=180)  # 3 minute timeout
                exit_code = result.get('StatusCode', -1)
                
                # Get output BEFORE removing container
                output = container.logs().decode('utf-8', errors='ignore')
                
                # Now we can safely remove the container
                try:
                    container.remove(force=True)
                except Exception as e:
                    print(f"[Docker Warning] Failed to remove container: {e}")
                
                # Parse JSON output (last line should be JSON)
                lines = output.strip().split('\n')
                json_output = None
                
                # Find the JSON result - try multiple strategies
                # Strategy 1: Look for lines starting with '{'
                for line in reversed(lines):
                    line = line.strip()
                    if line.startswith('{'):
                        try:
                            json_output = json.loads(line)
                            print(f"[Docker] ✓ Parsed JSON successfully from line")
                            break
                        except json.JSONDecodeError as e:
                            print(f"[Docker Debug] JSON parse failed for line: {e}")
                            continue
                
                # Strategy 2: Try to find JSON block (lines between first { and last })
                if json_output is None:
                    try:
                        # Find first { and last }
                        start_idx = None
                        end_idx = None
                        for i, line in enumerate(lines):
                            if '{' in line and start_idx is None:
                                start_idx = i
                            if '}' in line:
                                end_idx = i
                        
                        if start_idx is not None and end_idx is not None:
                            json_str = '\n'.join(lines[start_idx:end_idx+1])
                            json_output = json.loads(json_str)
                            print(f"[Docker] ✓ Parsed JSON successfully from block")
                    except Exception as e:
                        print(f"[Docker Debug] Block JSON parse failed: {e}")
                
                if json_output is None:
                    # If no JSON found, show the output for debugging
                    print(f"[Docker] Failed to parse JSON from output")
                    print(f"[Docker] Container output:\n{output}")
                    return {
                        "error": "Failed to parse benchmark results",
                        "output": output,
                        "exit_code": exit_code
                    }
                
                print(f"[Docker] ✓ Benchmark completed successfully!")
                return json_output
                
            except Exception as e:
                print(f"[Docker Error] Container execution failed: {e}")
                try:
                    # Try to get logs if possible
                    logs = container.logs().decode('utf-8', errors='ignore')
                    print(f"[Docker] Container logs:\n{logs}")
                    
                    # Try to remove container
                    container.remove(force=True)
                except Exception as cleanup_error:
                    print(f"[Docker Warning] Cleanup error: {cleanup_error}")
                
                return {"error": f"Container execution error: {str(e)}"}
            
        except Exception as e:
            print(f"[Docker Error] Benchmark failed: {e}")
            return {"error": str(e)}
        
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"[Docker Warning] Failed to cleanup temp dir: {e}")
    
    def cleanup(self):
        """Remove Docker image and free resources"""
        try:
            if self.image_built:
                print(f"[Docker] Removing image '{self.image_name}'...")
                self.client.images.remove(self.image_name, force=True)
                print("[Docker] ✓ Image removed successfully!")
                self.image_built = False
        except docker.errors.ImageNotFound:
            print("[Docker] Image not found, nothing to clean up.")
        except Exception as e:
            print(f"[Docker Warning] Cleanup error: {e}")
    
    def __enter__(self):
        """Context manager entry - ensure image exists"""
        self.ensure_image_exists()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup (optional)"""
        # Note: We don't auto-cleanup here because the image should persist
        # between multiple benchmark runs in the same session
        return False


# Global instance for the application
_manager_instance = None

def get_manager() -> DockerBenchmarkManager:
    """Get or create the global DockerBenchmarkManager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = DockerBenchmarkManager()
        # Build image on first access
        _manager_instance.ensure_image_exists()
    return _manager_instance

def cleanup_manager():
    """Cleanup the global manager instance"""
    global _manager_instance
    if _manager_instance is not None:
        _manager_instance.cleanup()
        _manager_instance = None

# Convenience functions for easy integration
def get_system_info() -> str:
    """Get system info for code generation prompts"""
    try:
        manager = get_manager()
        return manager.get_system_info()
    except Exception as e:
        print(f"[Docker Warning] Could not get system info: {e}")
        return "Linux x86_64"

def get_compile_command(language: str) -> str:
    """Get compile command for a specific language"""
    try:
        manager = get_manager()
        return manager.get_compile_command(language)
    except Exception as e:
        print(f"[Docker Warning] Could not get compile command: {e}")
        return ""

def run_benchmark(python_code: str, cpp_code: str, java_code: str, rust_code: str) -> Dict:
    """Run benchmark on all code files"""
    try:
        manager = get_manager()
        return manager.run_benchmark(python_code, cpp_code, java_code, rust_code)
    except Exception as e:
        print(f"[Docker Error] Benchmark failed: {e}")
        return {
            "error": str(e),
            "python": {"success": False, "error": str(e)},
            "cpp": {"success": False, "error": str(e)},
            "java": {"success": False, "error": str(e)},
            "rust": {"success": False, "error": str(e)}
        }


if __name__ == "__main__":
    """Test the Docker setup"""
    print("Testing Docker setup...")
    
    # Test code samples
    test_python = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(35):
    print(f"fib({i}) = {fibonacci(i)}")
"""
    
    test_cpp = """
#include <iostream>
using namespace std;

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    for (int i = 0; i < 35; i++) {
        cout << "fib(" << i << ") = " << fibonacci(i) << endl;
    }
    return 0;
}
"""
    
    test_rust = """
fn fibonacci(n: i32) -> i32 {
    if n <= 1 { return n; }
    fibonacci(n-1) + fibonacci(n-2)
}

fn main() {
    for i in 0..35 {
        println!("fib({}) = {}", i, fibonacci(i));
    }
}
"""
    
    test_java = """
public class Main {
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n-1) + fibonacci(n-2);
    }
    
    public static void main(String[] args) {
        for (int i = 0; i < 35; i++) {
            System.out.println("fib(" + i + ") = " + fibonacci(i));
        }
    }
}
"""
    
    # Run test
    try:
        manager = get_manager()
        results = manager.run_benchmark(test_python, test_cpp, test_java, test_rust)
        
        print("\n" + "="*60)
        print("BENCHMARK RESULTS")
        print("="*60)
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        # Optional cleanup
        cleanup_manager()