import discord
from discord.ext import commands

class GuildManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guildInfos = {} # {guild id: guildInfo}
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.guildInfos[guild.id] = GuildInfo(guild.id)
            

    def get_guild_info(self, id):
        return self.guildInfos[id]
        
        
        
class GuildInfo:
    def __init__(self, id):
        self.id = id
        self.musicInfo = MusicInfo()
        

    def clear_music_info(self):
        self.musicInfo.clear_all()
        
        

class MusicInfo:
    def __init__(self):
        self.songInfoQueue = []
        self.currentSongInfo = {}
        self.isLooping = False
        
        
    def clear_queue(self):
        self.songInfoQueue.clear()
        
        
    def clear_current_song_info(self):
        self.currentSongInfo = {}
        
        
    def clear_all(self):
        self.clear_queue()
        self.clear_current_song_info()
        
        
    def loop(self):
        self.isLooping = not self.isLooping
        
        
    def add_song_info(self, songInfo):
        self.songInfoQueue.append(songInfo)
        
        
    def get_current_song_info(self):
        return self.currentSongInfo
    

    def get_all_song_info_message(self):
        message = ""
        i = 0
        for songInfo in self.songInfoQueue:
            i += 1
            message += str(i) + ". " + songInfo["title"] + "\n"
        return message
        
        
        
def setup(bot):
    bot.add_cog(GuildManager(bot))