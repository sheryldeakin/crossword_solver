from grid.grid_builder import CrosswordGrid

def main():
    print("🧠 Welcome to the AI Crossword Solver.")
    print("This is a placeholder. Add your pipeline call here.")

    file_path = "data/puzzle_samples/processed_puzzle_samples/crossword_2022_07_03.csv"
    crossword = CrosswordGrid(file_path)
    crossword.display_grid()

    print("\nSample across clue:")
    print(crossword.across_clues[1])  # Replace with an actual number from your file

if __name__ == "__main__":
    main()

    
