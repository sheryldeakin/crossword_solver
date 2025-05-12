import time
import pandas as pd
import pygame
from gui.grid_visualizer import CrosswordVisualizer
from grid.grid_builder import CrosswordGrid

def start_solving(crossword, visualizer):
    for clue in crossword.clue_df.itertuples():
        clue_id = clue.number_direction  # e.g. "12-Across"
        visualizer.highlight_clues([clue_id])  # 🔥 Highlight current clue
    
        for (x, y) in clue.coordinate_set:
            while getattr(visualizer, "paused", False):
                pygame.time.wait(10)  # Wait while paused
            visualizer.update_cell(y, x, "A")
            time.sleep(0.05)
            
    visualizer.highlight_clues([]) 

def main():
    print("🧠 Welcome to the AI Crossword Solver.")
    print("This is a placeholder. Add your pipeline call here.\n")

    file_path = "crossword_solver\data\puzzle_samples\processed_puzzle_samples\crossword_2022_06_05.csv"
    clue_df = pd.read_csv(file_path)     # read the CSV into a DataFrame
    crossword = CrosswordGrid(clue_df)   # pass the DataFrame
    crossword.display()

    visualizer = CrosswordVisualizer(crossword)

    # Launch visualization in separate thread or inline for now
    from threading import Thread
    # Thread(target=visualizer.run).start()
    # # Hook up the start button
    visualizer.on_start = lambda: Thread(target=start_solving, args=(crossword, visualizer)).start()

    visualizer.run()

    print("\nSample across clue:")
    print(crossword.across_clues[1])  # Replace with an actual number from your file

if __name__ == "__main__":
    main()

    
