import tkinter as tk
from tkinter import Canvas, Label
from gameboard import GameBoard, Player, Color, Direction
from llm import get_llm_proposed_moves
from transcript_manager import TranscriptManager
from PIL import Image, ImageTk


class GameBoardUI:
    def __init__(self, master, game_board=None):
        self.master = master
        self.master.title("Game Board Display")
        self.master.geometry("600x600")

        # Initialize the game board (use provided one or create new)
        self.game_board = game_board if game_board is not None else GameBoard()
        self.transcript = TranscriptManager()

        # Create canvas
        self.canvas = Canvas(master, width=500, height=500, bg="white")
        self.canvas.pack(padx=50, pady=50)

        # Calculate cell size
        self.cell_size = 500 // self.game_board.size

        # Map Color enum to hex colors
        self.color_map = {
            Color.RED: "#FF0000",
            Color.GREEN: "#00FF00",
            Color.BLUE: "#0000FF",
            Color.YELLOW: "#FFD700",
        }

        # Enemy pieces are all black
        self.enemy_color = "#000000"

        self.game_over_frame = None

        self.draw_board()

    def set_gameboard(self, game_board):
        """Set a new gameboard and update the display."""
        self.game_board = game_board
        self.cell_size = (
            500 // self.game_board.size
        )  # Recalculate in case board size changed
        self.draw_board()

    def update_display(self):
        """Refresh the display to show current game board state."""
        self.draw_board()

    def refresh(self):
        """Alias for update_display() for convenience."""
        self.update_display()

    def draw_board(self):
        """Draw the game board and pieces."""
        self.canvas.delete("all")

        # Draw grid lines
        for i in range(self.game_board.size + 1):
            x = i * self.cell_size
            y = i * self.cell_size

            # Vertical lines
            self.canvas.create_line(
                x, 0, x, self.game_board.size * self.cell_size, fill="gray", width=1
            )
            # Horizontal lines
            self.canvas.create_line(
                0, y, self.game_board.size * self.cell_size, y, fill="gray", width=1
            )

        # Draw pieces
        for row in range(self.game_board.size):
            for col in range(self.game_board.size):
                piece = self.game_board.get_piece_at(row, col)
                if piece:
                    self.draw_piece(piece, row, col)

    def draw_piece(self, piece, row, col):
        """Draw a single piece on the board."""
        x1 = col * self.cell_size + 5
        y1 = row * self.cell_size + 5
        x2 = x1 + self.cell_size - 10
        y2 = y1 + self.cell_size - 10

        # Determine color
        if piece.owner == Player.PLAYER:
            # Use the piece's actual color
            color = self.color_map[piece.color]
        else:
            color = self.enemy_color

        # Draw piece as circle
        self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black", width=2)

        # Add piece ID as text in the center
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        text_color = "white" if piece.owner == Player.ENEMY else "black"

        self.canvas.create_text(
            center_x,
            center_y,
            text=str(piece.id),
            fill=text_color,
            font=("Arial", 10, "bold"),
        )

    def show_game_over(self, victor=None):
        """Display a game over screen with victory/defeat image as a transparent overlay."""
        # Destroy any existing game over frame to prevent stacking
        if self.game_over_frame:
            self.game_over_frame.destroy()
            self.game_over_frame = None

        # Don't clear the canvas to keep the final board state visible.

        # Create a frame for the game over screen. This will act as an overlay.
        # A smaller, solid-color frame lets the board be seen around it.
        self.game_over_frame = tk.Frame(self.master, bg="black", bd=2, relief=tk.RAISED)
        self.game_over_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Determine the message and image based on the victor
        subtitle_bg = "black"
        if victor == Player.PLAYER:
            message = "🎉 VICTORY! 🎉"
            subtitle = "You made the first capture!"
            message_color = "#00FF00"  # Green for victory
        elif victor == Player.ENEMY:
            message = "💀 DEFEAT 💀"
            subtitle = "Enemy made the first capture!"
            message_color = "#FF0000"  # Red for defeat
            subtitle_bg = "#8B0000"  # Dark red to highlight the defeat condition
        else:
            message = "🎲 GAME OVER 🎲"
            subtitle = "The game has ended"
            message_color = "#FFFFFF"  # White for neutral

        # Create title label
        title_label = Label(
            self.game_over_frame,
            text=message,
            font=("Arial", 32, "bold"),
            fg=message_color,
            bg="black",
        )
        title_label.pack(pady=(20, 10), padx=20)

        # Create subtitle label
        subtitle_label = Label(
            self.game_over_frame,
            text=subtitle,
            font=("Arial", 16),
            fg="white",
            bg=subtitle_bg,
        )
        subtitle_label.pack(pady=(0, 20), padx=10, fill="x", ipady=5)

        # Try to load and display actual images
        image_loaded = False
        image_label = None
        image_path = None

        try:
            if victor == Player.PLAYER:
                image_path = "assets/YOU_WIN.jpg"
            elif victor == Player.ENEMY:
                image_path = "assets/YOU_LOSE.jpg"

            if image_path:
                pil_image = Image.open(image_path)
                pil_image = pil_image.resize((300, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)

                image_label = Label(self.game_over_frame, image=photo, bg="black")
                image_label.image = photo
                image_label.pack(pady=10)
                image_loaded = True

        except (FileNotFoundError, Exception) as e:
            print(f"Could not load image: {e}")
            image_loaded = False

        # Fallback to custom graphics if images couldn't be loaded
        if not image_loaded:
            # Create a canvas for the fallback visual element
            image_canvas = Canvas(
                self.game_over_frame,
                width=300,
                height=150,
                bg="black",
                highlightthickness=0,
            )
            image_canvas.pack(pady=10)

            if victor == Player.PLAYER:
                # Draw a victory crown/trophy (adjusted for smaller canvas)
                image_canvas.create_rectangle(
                    125, 120, 175, 150, fill="#FFD700", outline="#FFA500", width=2
                )
                image_canvas.create_oval(
                    100, 70, 200, 130, fill="#FFD700", outline="#FFA500", width=3
                )
                image_canvas.create_oval(
                    80, 90, 100, 110, fill="", outline="#FFA500", width=3
                )
                image_canvas.create_oval(
                    200, 90, 220, 110, fill="", outline="#FFA500", width=3
                )
                points = [150, 50, 140, 70, 160, 70]
                image_canvas.create_polygon(
                    points, fill="#FFD700", outline="#FFA500", width=2
                )

            elif victor == Player.ENEMY:
                # Draw a defeat skull (adjusted for smaller canvas)
                image_canvas.create_oval(
                    110, 50, 190, 120, fill="#CCCCCC", outline="#999999", width=2
                )
                image_canvas.create_oval(125, 70, 140, 90, fill="black")
                image_canvas.create_oval(160, 70, 175, 90, fill="black")
                image_canvas.create_polygon(
                    [150, 95, 145, 105, 155, 105], fill="black"
                )
                for i in range(6):
                    x = 130 + i * 8
                    image_canvas.create_line(
                        x, 110, x + 4, 120, x + 8, 110, fill="black", width=2
                    )
            else:
                # Draw a neutral game piece
                image_canvas.create_oval(
                    125, 50, 175, 100, fill="#888888", outline="white", width=3
                )
                image_canvas.create_text(
                    150, 75, text="?", fill="white", font=("Arial", 24, "bold")
                )

        # Create restart/exit buttons
        button_frame = tk.Frame(self.game_over_frame, bg="black")
        button_frame.pack(pady=20)

        restart_button = tk.Button(
            button_frame,
            text="New Game",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            command=self.restart_game,
        )
        restart_button.pack(side=tk.LEFT, padx=10)

        exit_button = tk.Button(
            button_frame,
            text="Exit",
            font=("Arial", 14, "bold"),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10,
            command=self.master.quit,
        )
        exit_button.pack(side=tk.LEFT, padx=10)

    def restart_game(self):
        """Restart the game with a new board."""
        # Clear the game over frame if it exists
        if self.game_over_frame:
            self.game_over_frame.destroy()
            self.game_over_frame = None

        # Reset the game board using the setter to ensure cell size is recalculated
        from gameboard import GameBoard

        self.set_gameboard(GameBoard())


def get_piece(game_board, player, color):
    """Find and return the red player piece."""
    for piece in game_board.pieces.values():
        if piece.owner == player and (color is None or piece.color == color):
            return piece
    return None


def demo_move_red_piece(ui):
    """Demo function that moves the red piece up every 2 seconds."""
    red_piece = get_piece(ui.game_board, Player.PLAYER, Color.RED)

    if red_piece is None:
        print("Demo ended: Red piece not found")
        return
    ai_selected_moves = get_llm_proposed_moves(ui.game_board, Player.ENEMY, "  ")

    # Try to move the red piece up
    move_successful = ui.game_board.execute_turn(
        {
            red_piece.id: Direction.UP,
            **ai_selected_moves,
        }
    )

    if move_successful:
        ui.update_display()
        print(f"Red piece moved to position {red_piece.position}")

        # Schedule the next move in 2 seconds
        ui.master.after(2000, lambda: demo_move_red_piece(ui))
    else:
        print(f"Demo ended: Red piece at {red_piece.position} cannot move up anymore")


def main():
    root = tk.Tk()
    app = GameBoardUI(root)

    # Move the first black piece down and 3 to the right
    # black_piece = get_piece(app.game_board, Player.ENEMY, None)
    # if black_piece:
    #     app.game_board.move_piece(black_piece.id, Direction.DOWN)
    #     app.game_board.move_piece(black_piece.id, Direction.RIGHT)
    #     app.game_board.move_piece(black_piece.id, Direction.RIGHT)

    # Move the black pieces based on the ai instructions

    # Start the demo animation after 1 second
    root.after(1000, lambda: demo_move_red_piece(app))

    root.mainloop()


if __name__ == "__main__":
    main()
