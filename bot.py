import pyautogui
import time
import asyncio
from collections import defaultdict
from twitchio.ext import commands
from ppadb.client import Client as AdbClient
import win32gui
import random

# Twitch Bot Configuration
TWITCH_NICKNAME = "littleindianboi637"
TWITCH_TOKEN =   # Get from https://twitchapps.com/tmi/
TWITCH_CHANNEL = "littleindianboi637"

pagename = "SM-G990U1"
hwnd = win32gui.FindWindow(None, pagename)

# ADB Phone Tap Coordinates
TAP_COORDS = {
    "1": (200, 1160),
    "2": (500, 1160),
    "3": (800, 1160),
}

# Pixel Check Configuration
PIXEL_COORD = (1169, 947)
TARGET_COLOR = (255, 84, 235)


def check_pixel():
    """Check if the specific pixel is the target color."""
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
       #print("Already in foreground.")
        weuh=1

    screenshot = pyautogui.screenshot()
    pixel_color = screenshot.getpixel(PIXEL_COORD)
    #print(pixel_color)
    if pixel_color[0] > 250 and 80 < pixel_color[1] < 90 and 225 < pixel_color[2] < 245:
        return True
    else:
        return False


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix="!", nick=TWITCH_NICKNAME, initial_channels=[TWITCH_CHANNEL])
        self.votes = defaultdict(set)  # Stores votes, ensuring 1 per user per period

    async def event_message(self, message):
        """Handle incoming Twitch chat messages."""
        if message.echo:
            return  # Ignore bot's own messages

        for num in ["1", "2", "3"]:
            if num in message.content:
                self.votes[num].add(message.author.name)

    async def collect_votes(self):
        """Collect Twitch chat messages for 7 seconds and then send a message."""
        self.votes.clear()
        await asyncio.sleep(7)
        winner = self.get_winner()

        # Send message after voting ends
        await self.send_message("Voting ended!")

        return winner

    def get_winner(self):
        """Determine which number has the most votes."""
        max_votes = 0
        winner = None
        for num, users in self.votes.items():
            if len(users) > max_votes:
                max_votes = len(users)
                winner = num
        return winner

    async def send_message(self, message):
        """Send a message to Twitch chat."""
        channel = self.get_channel(TWITCH_CHANNEL)
        if channel:
            await channel.send(message)
        else:
            print("Failed to send message: Bot is not connected to chat.")


def tap_phone(number):
    """Simulate a phone screen tap via ADB based on the winning number."""
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()

    if not devices:
        print("No ADB devices found!")
        return

    device = devices[0]  # Use the first connected device
    if number in TAP_COORDS:
        x, y = TAP_COORDS[number]
        device.input_tap(x, y)
        print(f"Tapped {number} at ({x}, {y})")


async def main():
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
                random_tap = str(random.randint(1, 3))
                tap_phone(random_tap)

        else:
            #print("Pixel not detected. Waiting...")
            ewut=1

        time.sleep(2)  # Check the pixel again every 2 seconds


if __name__ == "__main__":
    asyncio.run(main())
