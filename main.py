from clients.bot import DiscordBot
import cogs.channel as channel
import cogs.music as music
import cogs.guild as guild
import cogs.help as help

import os
from dotenv import load_dotenv
load_dotenv()

# Variable
token = os.getenv("TOKEN")
prefix = ["lun ", "lun"]
cogs = [guild, channel, music, help]

def main():
    bot = DiscordBot(command_prefix = prefix, help_command=None)
    
    for cog in cogs:
        cog.setup(bot)

    bot.run(token)
    
if __name__ == "__main__":
    main()