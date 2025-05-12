import pygame
import sys

CELL_SIZE = 40
FONT_SIZE = 24
GRID_PADDING = 2

RIGHT_PANEL_WIDTH = 500
PADDING = 10

BUTTON_HEIGHT = 50

class CrosswordVisualizer:
    def __init__(self, crossword_grid):
            pygame.init()
            self.crossword = crossword_grid
            self.grid = crossword_grid.grid
            self.height, self.width = self.grid.shape
            # self.window = pygame.display.set_mode((self.width * CELL_SIZE, self.height * CELL_SIZE))
            pygame.display.set_caption("Crossword Solver Visualizer")
            self.font = pygame.font.SysFont(None, FONT_SIZE)
            self.number_font = pygame.font.SysFont(None, 14)
            self.cell_numbers = self._build_cell_to_number_map()
            total_width = self.width * CELL_SIZE + RIGHT_PANEL_WIDTH
            total_height = max(self.height * CELL_SIZE + BUTTON_HEIGHT, 1000)
            self.window = pygame.display.set_mode((total_width, total_height))
            self.clue_font = pygame.font.SysFont(None, 16)  # smaller for sidebar clues
            self.scroll_offset = 0
            self.max_scroll = 0
            self.scroll_speed = 20
            self.paused = False
            self.active_clue_ids = set()  # e.g., {"12-Across", "5-Down"}


    def _build_cell_to_number_map(self):
        """Return {(row, col): clue_number} for start cells."""
        mapping = {}
        for _, row in self.crossword.clue_df.iterrows():
            r, c = row["start_row"], row["start_col"]
            mapping[(r, c)] = row["number"]
        return mapping
    
    def highlight_clues(self, clue_ids):
        """Set the currently active clues being solved."""
        self.active_clue_ids = set(clue_ids)
        self.draw_grid()

    
    def draw_clues(self):
        """Draws Across and Down clues in two side-by-side columns with scroll and greyed-out solved clues."""

        panel_start_x = self.width * CELL_SIZE + PADDING
        column_width = (RIGHT_PANEL_WIDTH - 3 * PADDING) // 2
        across_x = PADDING
        down_x = across_x + column_width + PADDING
        surface_width = RIGHT_PANEL_WIDTH - 2 * PADDING

        # Temporary surface to render all clues
        clue_surface_height = 5000  # large enough buffer; we’ll crop later
        clue_surface = pygame.Surface((surface_width, clue_surface_height))
        clue_surface.fill((255, 255, 255))

        y_across = 0
        y_down = 0

        total_height = 0

        def render_section(title, clues_dict, start_x, y):
            nonlocal total_height
            title_surface = self.font.render(title, True, (0, 0, 0))
            clue_surface.blit(title_surface, (start_x, y))
            y += title_surface.get_height() + 10

            clue_type = "Across" if title.lower() == "across" else "Down"

            # Determine solved clues
            solved_set = set()
            for _, row in self.crossword.clue_df.iterrows():
                coords = row["coordinate_set"]
                if all(self.grid[y_][x_] != " " and self.grid[y_][x_] != "■" for (x_, y_) in coords):
                    solved_set.add(row["number_direction"])

            # Sort: unsolved first, then solved
            clue_items = list(clues_dict.items())
            sorted_clues = sorted(
                clue_items,
                key=lambda item: (
                    f"{item[0]}-{clue_type}" in solved_set,  # False comes first
                    item[0]
                )
            )

            max_width = (RIGHT_PANEL_WIDTH - 3 * PADDING) // 2
            for number, clue in sorted_clues:
                nd = f"{number}-{clue_type}"
                is_solved = nd in solved_set
                is_active = nd in self.active_clue_ids

                text = f"{number}. {clue}"
                fg_color = (0, 0, 0)
                bg_color = None

                if is_solved:
                    fg_color = (150, 150, 150)
                if is_active:
                    bg_color = (255, 255, 180)  # light yellow

                # Word wrapping
                words = text.split()
                current_line = ""
                line_surfaces = []

                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    test_surface = self.clue_font.render(test_line, True, fg_color)
                    if test_surface.get_width() > max_width and current_line:
                        line_surfaces.append(self.clue_font.render(current_line, True, fg_color))
                        current_line = word
                    else:
                        current_line = test_line
                if current_line:
                    line_surfaces.append(self.clue_font.render(current_line, True, fg_color))

                # Draw background for full block if active
                if bg_color:
                    block_height = sum(s.get_height() for s in line_surfaces) + (len(line_surfaces) - 1) * 2 + 4
                    bg_rect = pygame.Rect(start_x - 5, y - 2, column_width + 10, block_height)
                    pygame.draw.rect(clue_surface, bg_color, bg_rect)

                for line_surface in line_surfaces:
                    clue_surface.blit(line_surface, (start_x, y))
                    y += line_surface.get_height() + 2


                y += 10  # extra padding between clues

            y += 12  # spacing after section
            total_height = max(total_height, y)
            return y


        height_across = render_section("Across", self.crossword.across_clues, across_x, y_across)
        height_down = render_section("Down", self.crossword.down_clues, down_x, y_down)
        total_height = max(height_across, height_down)

        # Update scroll limit
        visible_clue_area = self.window.get_height() - BUTTON_HEIGHT - PADDING
        self.max_scroll = max(0, total_height - visible_clue_area)
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

        # Blit visible portion of clue_surface to the main window
        visible_rect = pygame.Rect(0, self.scroll_offset, surface_width, visible_clue_area)
        dest_x = self.width * CELL_SIZE + PADDING
        self.window.blit(clue_surface.subsurface(visible_rect), (dest_x, PADDING))

        # Draw scrollbar
        if self.max_scroll > 0:
            bar_x = self.width * CELL_SIZE + RIGHT_PANEL_WIDTH - 10
            clue_top_y = PADDING
            clue_bottom_y = self.window.get_height() - BUTTON_HEIGHT - PADDING
            bar_height = clue_bottom_y - clue_top_y

            scrollbar_rect = pygame.Rect(bar_x, clue_top_y, 6, bar_height)
            pygame.draw.rect(self.window, (200, 200, 200), scrollbar_rect)

            visible_ratio = bar_height / (bar_height + self.max_scroll)
            thumb_height = max(30, int(bar_height * visible_ratio))
            scroll_ratio = self.scroll_offset / self.max_scroll if self.max_scroll else 0
            thumb_y = int(clue_top_y + (bar_height - thumb_height) * scroll_ratio)
            thumb_rect = pygame.Rect(bar_x, thumb_y, 6, thumb_height)
            pygame.draw.rect(self.window, (100, 100, 100), thumb_rect)


    def draw_control_panel(self):
        """Draws control buttons like Start and Quit under the grid."""
        y_offset = self.height * CELL_SIZE + 10

        # Start Button
        start_rect = pygame.Rect(PADDING, y_offset, 100, 30)
        pygame.draw.rect(self.window, (0, 120, 0), start_rect)  # green
        pygame.draw.rect(self.window, (0, 0, 0), start_rect, 2)
        start_text = self.font.render("Start", True, (255, 255, 255))
        self.window.blit(start_text, start_text.get_rect(center=start_rect.center))

        # Quit Button
        quit_rect = pygame.Rect(PADDING + 120, y_offset, 100, 30)
        pygame.draw.rect(self.window, (200, 0, 0), quit_rect)  # red
        pygame.draw.rect(self.window, (0, 0, 0), quit_rect, 2)
        quit_text = self.font.render("Quit", True, (255, 255, 255))
        self.window.blit(quit_text, quit_text.get_rect(center=quit_rect.center))

        # Pause Button
        pause_rect = pygame.Rect(PADDING + 240, y_offset, 100, 30)
        pygame.draw.rect(self.window, (100, 100, 200), pause_rect)  # blue
        pygame.draw.rect(self.window, (0, 0, 0), pause_rect, 2)

        pause_label = "Paused" if self.paused else "Pause"
        pause_text = self.font.render(pause_label, True, (255, 255, 255))
        self.window.blit(pause_text, pause_text.get_rect(center=pause_rect.center))


        # Save for click detection
        self.quit_button_rect = quit_rect
        self.start_button_rect = start_rect
        self.pause_button_rect = pause_rect

        # ------------------------
        # Progress Bar
        # ------------------------
        bar_width = 300
        bar_height = 20
        bar_x = PADDING
        bar_y = y_offset + 40

        # Background
        pygame.draw.rect(self.window, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height))

        # Compute progress
        fillable = (self.grid != "■").sum()
        filled = ((self.grid != "■") & (self.grid != " ")).sum()
        percent = (filled / fillable) if fillable > 0 else 0

        # Filled bar
        filled_width = int(bar_width * percent)
        pygame.draw.rect(self.window, (0, 180, 0), (bar_x, bar_y, filled_width, bar_height))

        # Text label
        percent_text = self.font.render(f"{int(percent * 100)}%", True, (0, 0, 0))
        self.window.blit(percent_text, (bar_x + bar_width + 10, bar_y - 2))

        # ------------------------
        # Clue Progress (X / Y)
        # ------------------------
        solved = 0
        total = len(self.crossword.clue_df)

        for _, row in self.crossword.clue_df.iterrows():
            coords = row["coordinate_set"]
            if all(self.grid[y][x] != " " and self.grid[y][x] != "■" for (y, x) in coords):
                solved += 1

        clue_text = self.font.render(f"{solved} / {total} clues solved", True, (0, 0, 0))
        self.window.blit(clue_text, (PADDING, bar_y + bar_height + 10))



    def draw_grid(self):
        self.window.fill((255, 255, 255))  # white background
        active_coords = set()
        for clue_id in self.active_clue_ids:
            for _, row in self.crossword.clue_df.iterrows():
                if row["number_direction"] == clue_id:
                    # coordinate_set is [(x, y)], but grid is grid[y][x], so row = y, col = x
                    active_coords.update((row_, col_) for (col_, row_) in row["coordinate_set"])


        for row in range(self.height):
            for col in range(self.width):
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell = self.grid[row][col]

                if cell == "■":
                    pygame.draw.rect(self.window, (0, 0, 0), rect)
                    continue

                # Background
                pygame.draw.rect(self.window, (255, 255, 255), rect)

                # Highlight if active
                if (row, col) in active_coords:
                    pygame.draw.rect(self.window, (255, 255, 180), rect)

                # Grid border
                pygame.draw.rect(self.window, (0, 0, 0), rect, GRID_PADDING)


                if (row, col) in self.cell_numbers:
                    number = str(self.cell_numbers[(row, col)])
                    number_surface = self.number_font.render(number, True, (0, 0, 0))
                    self.window.blit(number_surface, (col * CELL_SIZE + 5, row * CELL_SIZE + 3))

                if cell != " ":
                    text_surface = self.font.render(cell, True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.window.blit(text_surface, text_rect)

        self.draw_clues()
        self.draw_control_panel()
        pygame.display.flip()

    def on_start(self):
    # Placeholder for now — override or assign externally
        pass


    def run(self):
        try:
            running = True
            self.draw_grid()
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click
                            if hasattr(self, "quit_button_rect") and self.quit_button_rect.collidepoint(event.pos):
                                running = False
                            elif hasattr(self, "start_button_rect") and self.start_button_rect.collidepoint(event.pos):
                                print("▶️ Start button clicked!")
                                self.on_start()  # call placeholder method
                            elif hasattr(self, "pause_button_rect") and self.pause_button_rect.collidepoint(event.pos):
                                self.paused = not getattr(self, "paused", False)
                                print("⏸️ Paused" if self.paused else "▶️ Resumed")
                                self.draw_grid()

                        elif event.button == 4:
                            self.scroll_offset = max(self.scroll_offset - self.scroll_speed, 0)
                            self.draw_grid()
                        elif event.button == 5:
                            self.scroll_offset = min(self.scroll_offset + self.scroll_speed, self.max_scroll)
                            self.draw_grid()

                        elif event.button == 5:
                            self.scroll_offset = min(self.scroll_offset + self.scroll_speed, self.max_scroll)
                            self.draw_grid()
                pygame.time.delay(10)
            pygame.quit()
            sys.exit()
        except Exception as e:
            print("Error in run loop:", e)
            import traceback
            traceback.print_exc()



    def update_cell(self, row, col, letter):
        """Call this method to update the display during solving."""
        self.grid[row][col] = letter
        self.draw_grid()
