import pyautogui
import time
import asyncio
from collections import defaultdict
from twitchio.ext import commands
from ppadb.client import Client as AdbClient
import win32gui
import random
import tkinter as tk
from PIL import Image, ImageTk
import threading

# Twitch Bot Configuration
TWITCH_NICKNAME = "littleindianboi637"
TWITCH_TOKEN = "8q9y75jav8klrekhn2rrqaiw7pstiq"  # Replace with your Twitch token
TWITCH_CHANNEL = "littleindianboi637"

pagename = "SM-G990U1"
hwnd = win32gui.FindWindow(None, pagename)

# Grid Configuration (A1 to F6)
GRID_COLUMNS = ["1", "2", "3", "4", "5", "6"]
GRID_ROWS = ["A", "B", "C", "D", "E", "F"]
GRID_SPACES = [f"{row}{col}" for row in GRID_ROWS for col in GRID_COLUMNS]

# ADB Phone Tap Coordinates (Modify as needed)
TAP_COORDS = {
    "A1": (225,760), "A2": (359, 760), "A3": (480, 760), "A4": (600, 760), "A5": (730, 760), "A6": (860, 760),
    "B1": (225, 944), "B2": (359, 944), "B3": (480, 944), "B4": (600, 944), "B5": (730, 944), "B6": (860, 944),
    "C1": (225, 1111), "C2": (359, 1111), "C3": (480, 1111), "C4": (600, 1111), "C5": (730, 1111), "C6": (860, 1111),
    "D1": (225, 1300), "D2": (359, 1300), "D3": (480, 1300), "D4": (600, 1300), "D5": (730, 1300), "D6": (860,1300),
    "E1": (225, 1455), "E2": (359, 1455), "E3": (480, 1455), "E4": (600, 1455), "E5": (730, 1455), "E6": (860, 1455),
    "F1": (225, 1620), "F2": (359, 1620), "F3": (480, 1620), "F4": (600, 1620), "F5": (730, 1620), "F6": (860, 1620),
}

# Pixel Check Configuration
PIXEL_COORD1 = (1169, 947)
PIXEL_COORD2 = (888, 285)


def check_pixel():
    """Check if the specific pixel is the target color."""
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass

    screenshot = pyautogui.screenshot()
    pixel_color1 = screenshot.getpixel(PIXEL_COORD1)
    pixel_color2 = screenshot.getpixel(PIXEL_COORD2)
    return pixel_color1[0] > 250 and 80 < pixel_color1[1] < 90 and 225 < pixel_color1[2] < 245 and pixel_color2[0] > 250 and pixel_color2[1] >250  and pixel_color2[2] > 250


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix="!", nick=TWITCH_NICKNAME, initial_channels=[TWITCH_CHANNEL])
        self.votes = defaultdict(set)  # Store votes, ensuring 1 per user per period

    async def event_message(self, message):
        """Handle incoming Twitch chat messages."""
        if message.echo:
            return  # Ignore bot's own messages

        for space in GRID_SPACES:
            if space.lower() in message.content.lower():
                self.votes[space].add(message.author.name)

    async def collect_votes(self):
        """Collect votes for 12 seconds while showing the overlay."""
        self.votes.clear()
        overlay.show_overlay()  # Show the grid overlay
        await asyncio.sleep(12)
        overlay.hide_overlay()  # Hide the overlay

        return self.get_winner()

    def get_winner(self):
        """Determine which space has the most votes, resolving ties randomly."""
        max_votes = 0
        winners = []

        for space, users in self.votes.items():
            vote_count = len(users)
            if vote_count > max_votes:
                max_votes = vote_count
                winners = [space]
            elif vote_count == max_votes:
                winners.append(space)

        return random.choice(winners) if winners else None


class Overlay:
    """A tkinter-based overlay to display the PNG grid during voting."""

    def __init__(self, image_path):
        self.image_path = image_path
        self.overlay = None
        self.label = None
        self.tk_image = None
        self.width = 600  # Default width (modifiable)
        self.height = 600  # Default height (modifiable)

    def show_overlay(self):
        """Display the PNG overlay window."""
        if self.overlay:
            return  # Already open

        # Initialize the Tkinter window in a new thread
        def create_overlay():
            self.overlay = tk.Toplevel()
            self.overlay.overrideredirect(True)  # Remove window borders
            self.overlay.attributes("-topmost", True)  # Keep it on top
            self.overlay.attributes("-transparentcolor", "white")  # Make white transparent

            # Load and resize image
            image = Image.open(self.image_path)
            image = image.resize((self.width, self.height), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(image)

            # Display the image in a label
            self.label = tk.Label(self.overlay, image=self.tk_image, bg="white")
            self.label.pack()

            # Position the overlay
            screen_width = self.overlay.winfo_screenwidth()
            screen_height = self.overlay.winfo_screenheight()
            x_position = (screen_width - self.width) // 2
            y_position = (screen_height - self.height) // 2
            self.overlay.geometry(f"{self.width}x{self.height}+{x_position}+{y_position}")

            # Start the Tkinter main loop for this window
            self.overlay.mainloop()

        # Run the Tkinter window in a separate thread to keep UI responsive
        threading.Thread(target=create_overlay, daemon=True).start()

    def hide_overlay(self):
        """Close the overlay window."""
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None


def tap_phone(space):
    """Simulate a phone screen tap via ADB based on the winning grid space."""
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()

    if not devices:
        print("No ADB devices found!")
        return

    device = devices[0]  # Use the first connected device
    if space in TAP_COORDS:
        x, y = TAP_COORDS[space]
        device.input_tap(x, y)
        print(f"Tapped {space} at ({x}, {y})")


async def main():
    global overlay
    overlay = Overlay("grid.png")  # Modify this path

    bot = TwitchBot()
    bot.loop.create_task(bot.start())

    while True:
        if check_pixel():
            print("Pixel detected! Starting vote collection...")
            winner = await bot.collect_votes()
            if winner:
                print(f"Winner is {winner}! Tapping phone screen...")
                tap_phone(winner)
            else:
                print("No votes received.")
                random_tap = random.choice(GRID_SPACES)
                tap_phone(random_tap)

        time.sleep(2)  # Check pixel every 2 seconds


if __name__ == "__main__":
    asyncio.run(main())
