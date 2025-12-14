#!/usr/bin/env python3
import subprocess
import time
import json
import os
import sys

def compile_and_run_cpp(source_path):
    """Compile and run C++ code"""
    try:
        # Compile
        compile_cmd = ["g++", "-O2", source_path, "-o", "/app/code/cpp_program"]
        result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Compilation error: {result.stderr}",
                "execution_time": None
            }
        
        # Run and measure time
        start_time = time.perf_counter()
        run_result = subprocess.run(["/app/code/cpp_program"], 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=60)
        end_time = time.perf_counter()
        
        if run_result.returncode != 0:
            return {
                "success": False,
                "error": f"Runtime error: {run_result.stderr}",
                "execution_time": None
            }
        
        return {
            "success": True,
            "execution_time": end_time - start_time,
            "output": run_result.stdout.strip()
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Execution timeout",
            "execution_time": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time": None
        }

def compile_and_run_rust(source_path):
    """Compile and run Rust code"""
    try:
        # Compile
        compile_cmd = ["rustc", "-O", source_path, "-o", "/app/code/rust_program"]
        result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Compilation error: {result.stderr}",
                "execution_time": None
            }
        
        # Run and measure time
        start_time = time.perf_counter()
        run_result = subprocess.run(["/app/code/rust_program"], 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=60)
        end_time = time.perf_counter()
        
        if run_result.returncode != 0:
            return {
                "success": False,
                "error": f"Runtime error: {run_result.stderr}",
                "execution_time": None
            }
        
        return {
            "success": True,
            "execution_time": end_time - start_time,
            "output": run_result.stdout.strip()
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Execution timeout",
            "execution_time": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time": None
        }

def compile_and_run_java(source_path):
    """Compile and run Java code"""
    try:
        # Extract class name from file
        class_name = os.path.splitext(os.path.basename(source_path))[0]
        
        # Compile
        compile_cmd = ["javac", source_path]
        result = subprocess.run(compile_cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30,
                              cwd="/app/code")
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Compilation error: {result.stderr}",
                "execution_time": None
            }
        
        # Run and measure time
        start_time = time.perf_counter()
        run_result = subprocess.run(["java", class_name], 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=60,
                                   cwd="/app/code")
        end_time = time.perf_counter()
        
        if run_result.returncode != 0:
            return {
                "success": False,
                "error": f"Runtime error: {run_result.stderr}",
                "execution_time": None
            }
        
        return {
            "success": True,
            "execution_time": end_time - start_time,
            "output": run_result.stdout.strip()
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Execution timeout",
            "execution_time": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time": None
        }

def run_python(source_path):
    """Run Python code"""
    try:
        # Run and measure time
        start_time = time.perf_counter()
        run_result = subprocess.run(["python3", source_path], 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=60)
        end_time = time.perf_counter()
        
        if run_result.returncode != 0:
            return {
                "success": False,
                "error": f"Runtime error: {run_result.stderr}",
                "execution_time": None
            }
        
        return {
            "success": True,
            "execution_time": end_time - start_time,
            "output": run_result.stdout.strip()
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Execution timeout",
            "execution_time": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time": None
        }

def main():
    results = {}
    
    # Check which files exist and run them
    code_dir = "/app/code"
    
    # Python
    python_file = os.path.join(code_dir, "code.py")
    if os.path.exists(python_file):
        print("Running Python code...", file=sys.stderr)
        results["python"] = run_python(python_file)
    else:
        results["python"] = {"success": False, "error": "File not found", "execution_time": None}
    
    # C++
    cpp_file = os.path.join(code_dir, "code.cpp")
    if os.path.exists(cpp_file):
        print("Compiling and running C++ code...", file=sys.stderr)
        results["cpp"] = compile_and_run_cpp(cpp_file)
    else:
        results["cpp"] = {"success": False, "error": "File not found", "execution_time": None}
    
    # Rust
    rust_file = os.path.join(code_dir, "code.rs")
    if os.path.exists(rust_file):
        print("Compiling and running Rust code...", file=sys.stderr)
        results["rust"] = compile_and_run_rust(rust_file)
    else:
        results["rust"] = {"success": False, "error": "File not found", "execution_time": None}
    
    # Java
    java_file = os.path.join(code_dir, "Main.java")
    if os.path.exists(java_file):
        print("Compiling and running Java code...", file=sys.stderr)
        results["java"] = compile_and_run_java(java_file)
    else:
        results["java"] = {"success": False, "error": "File not found", "execution_time": None}

    print(json.dumps(results))
    

if __name__ == "__main__":
    main()