from clients.bot import DiscordBot
import cogs.channel as channel
import cogs.music as music
import cogs.guild as guild

import os
from dotenv import load_dotenv
load_dotenv()

# Variable
token = os.getenv("TOKEN")
prefix = ["lun "]
cogs = [guild, channel, music]

def main():
    bot = DiscordBot(command_prefix = prefix)
    
    for cog in cogs:
        cog.setup(bot)

    bot.run(token)
    
if __name__ == "__main__":
    main()