import numpy as np
import pandas as pd
from utils.validation import validate_clue_df

class CrosswordGrid:
    def __init__(self, clue_df: pd.DataFrame):
        validate_clue_df(clue_df)
        self.clue_df = self._enrich_clue_df(clue_df)
        self.height = self.clue_df["end_row"].max() + 1
        self.width = self.clue_df["end_col"].max() + 1
        self.grid = self._generate_grid()

    def _generate_grid(self):
        grid = np.full((self.height, self.width), "■", dtype=str)
        for _, row in self.clue_df.iterrows():
            coords = row["coordinate_set"]
            for x, y in coords:
                grid[y][x] = " "
        return grid

    def _enrich_clue_df(self, df):
        df = df.copy()
        df["number_direction"] = df.apply(self._get_number_direction, axis=1)
        df["coordinate_set"] = df.apply(lambda row: self._get_coordinates(row), axis=1)
        return df

    def _get_number_direction(self, row):
        if row["start_row"] == row["end_row"]:
            return f"{row['number']}-Across"
        elif row["start_col"] == row["end_col"]:
            return f"{row['number']}-Down"
        else:
            raise ValueError(f"Invalid clue direction: {row}")

    def _get_coordinates(self, row):
        if "Across" in row["number_direction"]:
            return {(x, row["start_row"]) for x in range(row["start_col"], row["end_col"] + 1)}
        else:
            return {(row["start_col"], y) for y in range(row["start_row"], row["end_row"] + 1)}

    def display(self):
        """Full grid print with borders and fill percentage (replaces simple print)."""
        horizontal_border = "+" + "---" * self.width + "+"
        print(horizontal_border)
        for row in self.grid:
            row_display = "".join(f"[{cell}]" if cell != "■" else " ■ " for cell in row)
            print(f"|{row_display}|")
        print(horizontal_border)

    def detailed_print(self):
        """Detailed display with borders and progress info."""
        horizontal_border = "+" + "---" * self.width + "+"
        print(horizontal_border)

        print("Crossword Info")
        print(f"Grid size: {self.height} rows × {self.width} columns")

        if hasattr(self, 'table_name'):
            print(f"Title: {self.table_name}")

        percent_filled = self.calculate_completion_percentage_by_char()
        print(f"Fill progress: {percent_filled:.0f}%")

        print("\nGrid:")
        for row in self.grid:
            row_display = "".join(f"[{cell}]" if cell != "■" else " ■ " for cell in row)
            print(f"|{row_display}|")
        print(horizontal_border)

    def calculate_completion_percentage_by_char(self):
        """Returns % of non-black cells that are filled."""
        fillable = (self.grid != "■").sum()
        filled = ((self.grid != "■") & (self.grid != " ")).sum()
        return (filled / fillable * 100) if fillable else 0
    
    @property
    def across_clues(self):
        return {
            row["number"]: row["clue"]
            for _, row in self.clue_df.iterrows()
            if "Across" in row["number_direction"]
        }

    @property
    def down_clues(self):
        return {
            row["number"]: row["clue"]
            for _, row in self.clue_df.iterrows()
            if "Down" in row["number_direction"]
        }

