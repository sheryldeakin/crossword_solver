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
        for row in self.grid:
            print(' '.join(row))
