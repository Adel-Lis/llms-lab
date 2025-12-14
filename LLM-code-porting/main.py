"""
Code Porter - Main Entry Point

A tool for converting Python code to C++, Java, and Rust using AI,
then benchmarking performance across all languages.
"""

import signal 
import sys
import atexit

from setup_environment import get_manager, cleanup_manager
from ui import create_interface
from styles import CUSTOM_CSS


def cleanup():
    print("\n[Code Porter] Shutting down...")

    try:
        # Optional: Uncomment to remove Docker image on exit
        # cleanup_manager()

        print("[Code Porter] Server closed successfully.")
    except Exception as e:
        print(f"[Code Porter] Cleanup error: {e}")


def signal_handler(signum, frame):
    cleanup()
    sys.exit(0)


def main():
    try:
        print("[Code Porter] Initializing Docker environment...")
        get_manager()
        print("[Code Porter] Docker ready!")

        print("[Code Porter] Starting server on http://localhost:7860")
        app = create_interface()
        app.launch(server_port=7860, inbrowser=True, css=CUSTOM_CSS)

    except KeyboardInterrupt:
        print("[Code Porter] Closing app...")

    except Exception as e:
        print(f"[Code Porter] Error: {e}")
        cleanup()
        sys.exit(1)

    
if __name__ == "__main__":
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()