import pyautogui
import time
import asyncio
import random
from collections import defaultdict
from twitchio.ext import commands
from ppadb.client import Client as AdbClient
import win32gui


# Twitch Bot Configuration
TWITCH_NICKNAME = "littleindianboi637"
TWITCH_TOKEN = "8q9y75jav8klrekhn2rrqaiw7pstiq"  # Get from https://twitchapps.com/tmi/
TWITCH_CHANNEL = "littleindianboi637"

PIXEL_COORD1 = (1169, 947)
PIXEL_COORD2 = (888, 285)
pagename = "SM-G990U1"
hwnd = win32gui.FindWindow(None, pagename)

# Define Grid Positions (6x6 Chessboard Style)
GRID_LETTERS = ["A", "B", "C", "D", "E", "F"]
GRID_NUMBERS = ["1", "2", "3", "4", "5", "6"]

# Generate Grid Tap Coordinates (Modify these based on your screen)
TAP_COORDS = {}
base_x, base_y = 225, 760  # Adjust these to match screen alignment
spacing_x, spacing_y = 135, 180  # Adjust spacing as needed

for i, letter in enumerate(GRID_LETTERS):
    for j, number in enumerate(GRID_NUMBERS):
        TAP_COORDS[f"{letter}{number}"] = (base_x + j * spacing_x, base_y + i * spacing_y)

# Pixel Check Configuration
PIXEL_COORD = (1169, 947)
TARGET_COLOR = (255, 84, 235)


def check_pixel():
    """Check if the specific pixel is the target color."""
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass  # Already in foreground

    screenshot = pyautogui.screenshot()
    pixel_color1 = screenshot.getpixel(PIXEL_COORD1)
    pixel_color2 = screenshot.getpixel(PIXEL_COORD2)
    return pixel_color1[0] > 250 and 80 < pixel_color1[1] < 90 and 225 < pixel_color1[2] < 245 and pixel_color2[0] > 250 and pixel_color2[1] > 250 and pixel_color2[2] > 250


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix="!", nick=TWITCH_NICKNAME, initial_channels=[TWITCH_CHANNEL])
        self.votes = defaultdict(set)  # Stores votes, ensuring 1 per user per period
        self.votenumber = 1
    async def event_message(self, message):
        """Handle incoming Twitch chat messages."""
        if message.echo:
            return  # Ignore bot's own messages

        msg_content = message.content.upper().strip()
        if msg_content in TAP_COORDS:  # Check if message is a valid grid space
            self.votes[msg_content].add(message.author.name)

    async def collect_votes(self):
        """Collect Twitch chat messages for 12 seconds."""
        await self.send_message("Voting" + str(self.votenumber) + "Started!")
        self.votes.clear()
        await asyncio.sleep(12)

        winner = self.get_winner()
        await self.send_message("Voting" + str(self.votenumber)+  "Ended!")  # Announce voting end
        self.votenumber = self.votenumber+1
        if self.votenumber == 9:
            self.votenumber = 1
        return winner


    def get_winner(self):
        """Determine the most voted space. If tied, choose randomly."""
        max_votes = 0
        winning_options = []

        for grid_space, users in self.votes.items():
            num_votes = len(users)
            if num_votes > max_votes:
                max_votes = num_votes
                winning_options = [grid_space]
            elif num_votes == max_votes:
                winning_options.append(grid_space)

        return random.choice(winning_options) if winning_options else None

    async def send_message(self, message):
        """Send a message to Twitch chat."""
        channel = self.get_channel(TWITCH_CHANNEL)
        if channel:
            await channel.send(message)


def tap_phone(grid_space):
    """Simulate a phone screen tap via ADB based on the winning grid space."""
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()

    if not devices:
        print("No ADB devices found!")
        return

    device = devices[0]  # Use the first connected device
    if grid_space in TAP_COORDS:
        x, y = TAP_COORDS[grid_space]
        device.input_tap(x, y)
        print(f"Tapped {grid_space} at ({x}, {y})")
    time.sleep(1)


async def main():
    bot = TwitchBot()
    bot.loop.create_task(bot.start())

    while True:
        if check_pixel():
            print("Pixel detected! Starting vote collection...")
            winner = await bot.collect_votes()
            screenshot1 = pyautogui.screenshot()
            pixel_color3 = screenshot1.getpixel(PIXEL_COORD1)

            if pixel_color3[0] >250 and 80 < pixel_color3[1] < 90 and 225 < pixel_color3[2] < 245:
                if winner:
                    print(f"Winner is {winner}! Tapping phone screen...")
                    tap_phone(winner)
                else:
                    print("No votes received. Selecting random grid space.")
                    random_tap = random.choice(list(TAP_COORDS.keys()))
                    tap_phone(random_tap)

        time.sleep(2)  # Check the pixel again every 2 seconds


if __name__ == "__main__":
    asyncio.run(main())
