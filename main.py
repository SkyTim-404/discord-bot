from clients.bot import DiscordBot
import cogs.music as music

import os
from dotenv import load_dotenv
load_dotenv()

# Variable
token = os.getenv("ALLEN_WOKER_TOKEN")
prefix = ["+"]
cogs = [music]

def main():
    bot = DiscordBot(command_prefix = prefix)
    
    for cog in cogs:
        cog.setup(bot)

    bot.run(token)
    
if __name__ == "__main__":
    main()