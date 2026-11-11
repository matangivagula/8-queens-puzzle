import sys
import argparse

def main():
    if len(sys.argv) > 1 and sys.argv[1] != "--gui":
        from main import main as run_cli_experiments
        run_cli_experiments()
    else:
        # Launching GUI Visualizer
        print("Launching N-Queens GUI Visualizer.")
        import tkinter as tk
        from gui import NQueensGUI

        root = tk.Tk()
        app = NQueensGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()