import sys
import argparse

def main():
    # If command-line arguments are provided, run CLI experiment mode
    if len(sys.argv) > 1 and sys.argv[1] != "--gui":
        from main import main as run_cli_experiments
        run_cli_experiments()
    else:
        # Default behavior: Launch GUI Visualizer
        print("Launching N-Queens GUI Visualizer...")
        import tkinter as tk
        from gui import ColorfulNQueensGUI

        root = tk.Tk()
        app = ColorfulNQueensGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()