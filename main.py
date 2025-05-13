import time
import pandas as pd
import pygame
from gui.grid_visualizer import CrosswordVisualizer
from grid.grid_builder import CrosswordGrid


def start_solving(crossword, visualizer):
    visualizer.start_time = time.time()
    visualizer.elapsed_time = 0
    visualizer.timer_running = True

    for clue in crossword.clue_df.itertuples():
        clue_id = clue.number_direction
        answer = clue.answer  # Assumes you've renamed the column on load
        visualizer.highlight_clues([clue_id])

        # Place the entire word at once
        crossword.place_word(clue_id, answer)

        # Update the full grid in one step
        visualizer.draw_grid()

        # Pause briefly to simulate solving
        time.sleep(0.2)

        # Wait if paused
        while visualizer.paused:
            pygame.time.wait(10)

    visualizer.highlight_clues([])

    # Force a final redraw and timer stop if grid is complete
    visualizer.draw_grid()
    if visualizer.is_puzzle_filled():
        if visualizer.timer_running and visualizer.start_time is not None:
            visualizer.elapsed_time += time.time() - visualizer.start_time
            visualizer.start_time = None
        visualizer.timer_running = False



def main():
    print("🧠 Welcome to the AI Crossword Solver.")
    print("This is a placeholder. Add your pipeline call here.\n")

    file_path = "crossword_solver\data\puzzle_samples\processed_puzzle_samples\crossword_2022_06_05.csv"
    clue_df = pd.read_csv(file_path)     # read the CSV into a DataFrame
    clue_df = clue_df.rename(columns={"answer (optional column, for checking only)": "answer"})

    crossword = CrosswordGrid(clue_df)   # pass the DataFrame
    crossword.display()

    visualizer = CrosswordVisualizer(crossword)

    # Launch visualization in separate thread or inline for now
    from threading import Thread
    # Thread(target=visualizer.run).start()
    # # Hook up the start button
    visualizer.on_start = lambda: Thread(target=start_solving, args=(crossword, visualizer)).start()

    visualizer.run()
    crossword.display()

    print("\nSample across clue:")
    print(crossword.across_clues[1])  # Replace with an actual number from your file

if __name__ == "__main__":
    main()

    
