"""
Docker Setup Package - Contains Docker management and benchmark execution
"""

from .setup_environment import (
    get_manager,
    cleanup_manager,
    get_system_info,
    get_compile_command,
    run_benchmark
)

__all__ = [
    "get_manager",
    "cleanup_manager",
    "get_system_info",
    "get_compile_command",
    "run_benchmark"
]