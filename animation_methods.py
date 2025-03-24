
# Animation methods to be added to the PunchCardWidget class
# Add these methods to the PunchCardWidget class in simple_display.py

def animate_punch_card(self, punch_card_str):
    """Animate the punch card display using a diagonal animation.
    
    Args:
        punch_card_str: A string representation of the punch card pattern
                       with 'O' for holes and ' ' for no holes.
    """
    # Ensure animations don't run concurrently
    if self.animation_in_progress:
        logging.info("Animation already in progress, ignoring new request")
        return
        
    self.animation_in_progress = True
    
    # Parse the punch card string into a matrix of hole positions
    rows = punch_card_str.strip().split('\n')
    num_rows = len(rows)
    num_cols = max(len(row) for row in rows) if rows else 0
    
    logging.info(f"Animating punch card with {num_rows} rows and {num_cols} columns")
    
    if num_rows == 0 or num_cols == 0:
        logging.warning("Empty punch card matrix, cannot animate")
        self.animation_in_progress = False
        return
    
    # Create a matrix of hole positions where True = hole (O), False = no hole (space)
    holes = []
    for row in rows:
        hole_row = []
        for col in range(min(len(row), num_cols)):
            hole_row.append(row[col] == 'O')
        
        # Pad row if needed
        hole_row.extend([False] * (num_cols - len(hole_row)))
        holes.append(hole_row)
    
    # Ensure we have exactly 12 rows (12, 11, 0-9) for animation
    if len(holes) < 12:
        # Add empty rows if needed
        holes.extend([[False] * num_cols for _ in range(12 - len(holes))])
    elif len(holes) > 12:
        # Truncate if too many rows
        holes = holes[:12]
    
    # Calculate the number of diagonals to animate
    total_diagonals = num_rows + num_cols - 1
    
    # Start the animation timer
    self.animation_step = 0
    self.animation_total_steps = total_diagonals
    self.animation_holes = holes
    self.animation_timer.start(self.animation_speed)
    
    logging.info(f"Animation started with {total_diagonals} steps")

def _animation_step(self):
    """Process one step of the animation."""
    if self.animation_step >= self.animation_total_steps:
        # Animation complete
        self.animation_timer.stop()
        self.animation_in_progress = False
        logging.info("Animation complete")
        return
    
    # Current diagonal being animated
    diagonal = self.animation_step
    
    # For each row, column in the current diagonal, set the LED
    for row in range(min(self.num_rows, len(self.animation_holes))):
        col = diagonal - row
        if col >= 0 and col < self.num_cols:
            if row < len(self.animation_holes) and col < len(self.animation_holes[row]):
                self.set_led(row, col, self.animation_holes[row][col])
    
    # Move to the next diagonal
    self.animation_step += 1
