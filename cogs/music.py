import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import validators
import datetime

class Music(commands.Cog):
    
    YDL_OPTIONS = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "audioquality": 0,
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s", # download to directory
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0"
    }
    
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn"
    }
    
    def __init__(self, bot):
        self.bot = bot
        
    
    @commands.command(aliases = ["p"])
    async def play(self, ctx, *args):
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel")
            return
        info = self.get_video_info(*args)
        if info is None:
            await ctx.send("This is not a youtube video link")
            return
        musicInfo = self.get_music_info(ctx.guild.id)
        musicInfo.add_song_info(info)
        await self.bot.get_cog("Channel").join(ctx)
        voice_client = self.get_voice_client(ctx)
        if voice_client.is_playing():
            await ctx.send("enqueued " + info["title"])
            return
        self.play_next(ctx)
            
            
    @commands.command()
    async def clear(self, ctx):
        musicInfo = self.get_music_info(ctx.guild.id)
        musicInfo.clear_queue()
        await ctx.send("queue cleared")
    
    
    @commands.command(aliases = ["s"])
    async def skip(self, ctx):
        voice_client = self.get_voice_client(ctx)
        if voice_client is None:
            await ctx.send("Bot is not in a voice channel")
            return
        if voice_client.is_playing():
            musicInfo = self.get_music_info(ctx.guild.id)
            musicInfo.clear_current_song_info()
            voice_client.pause()
            self.play_next(ctx)
            await ctx.send("skipped")
        else:
            await ctx.send("Bot is not playing anything")
        
    
    @commands.command()
    async def stop(self, ctx):
        musicInfo = self.get_music_info(ctx.guild.id)
        musicInfo.clear_all()
        voice_client = self.get_voice_client(ctx)
        if voice_client is None:
            await ctx.send("Bot is not in a voice channel")
            return
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("Bot is not playing anything")
        
    
    @commands.command()
    async def pause(self, ctx):
        voice_client = self.get_voice_client(ctx)
        if voice_client is None:
            await ctx.send("Bot is not in a voice channel")
            return
        if voice_client.is_playing():
            voice_client.pause()
            await ctx.send("paused")
        elif voice_client.is_paused():
            await ctx.send("Bot is already paused")
        else:
            await ctx.send("Bot is not playing anything")
    
    
    @commands.command()
    async def resume(self, ctx):
        voice_client = self.get_voice_client(ctx)
        if voice_client is None:
            await ctx.send("Bot is not in a voice channel")
            return
        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send("resumed")
        elif voice_client.is_playing():
            await ctx.send("Bot is already playing")
        else:
            await ctx.send("Bot is not playing anything")
            
            
    @commands.command(aliases = ["q"])
    async def queue(self, ctx):
        message = self.get_music_info(ctx.guild.id).get_all_song_info_message()
        if message == "":
            await ctx.send("No music in queue")
        else:
            await ctx.send(message)
            
        
    @commands.command(aliases = ["np", "currentSong", "cs", "playing"])
    async def nowPlaying(self, ctx):
        try:
            currentSongInfo = self.get_music_info(ctx.guild.id).get_current_song_info()
            await ctx.send(f"Now playing {currentSongInfo['title']}")
        except:
            await ctx.send("Bot is not playing anything")
        
    
    @commands.command(aliases = ["l"])
    async def loop(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel")
            return
        
        musicInfo = self.get_music_info(ctx.guild.id)
        if musicInfo.isLooping:
            await ctx.send("Bot is now not looping")
        else:
            await ctx.send("Bot is now looping")
        musicInfo.loop()
    
        
    @commands.command()
    async def seek(self, ctx, time: str):
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel")
            return
        
        voice_client = self.get_voice_client(ctx)
        if not voice_client.is_playing():
            await ctx.send("Bot is not playing")
            return
        
        timeObj = None
        try:
            timeObj = datetime.datetime.strptime(time, "%M:%S")
        except ValueError:
            try:
                timeObj = datetime.datetime.strptime(time, "%H:%M:%S")
            except ValueError:
                await ctx.send("invalid input")
                return
            
        currentSongInfo = self.get_music_info(ctx.guild.id).get_current_song_info()
        videoDuration = currentSongInfo["duration"]
        inputTimeSeconds = (timeObj-datetime.datetime(1900, 1, 1)).total_seconds()
        
        if inputTimeSeconds > videoDuration:
            await ctx.send("out of range")
            return
        
        NEW_FFMPEG_OPTIONS = self.FFMPEG_OPTIONS.copy()
        NEW_FFMPEG_OPTIONS["before_options"] += " -ss {}".format(time)
        
        voice_client.pause()
        self.play_with_info(ctx, currentSongInfo, NEW_FFMPEG_OPTIONS)
        await ctx.send("seeked {}".format(time))
        
    
    def play_with_info(self, ctx, info, FFMPEG_OPTIONS):
        voice_client = self.get_voice_client(ctx)
        
        url = info["url"]
        
        voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        
    
    def play_next(self, ctx):
        musicInfo = self.get_music_info(ctx.guild.id)
        
        if not (musicInfo.isLooping and musicInfo.currentSongInfo):
            if len(musicInfo.songInfoQueue) == 0:
                musicInfo.clear_current_song_info()
                return
            else:
                musicInfo.currentSongInfo = musicInfo.songInfoQueue.pop(0)
            
        self.bot.loop.create_task(self.nowPlaying(ctx))
        self.play_with_info(ctx, musicInfo.currentSongInfo, self.FFMPEG_OPTIONS)
        
    
    def get_video_info(self, *args):
        try:
            info = None
            if validators.url(args[0]):
                if not "v=" in args[0]:
                    return None
                info = self.get_video_info_from_url(args[0])
            else:
                keyword = " ".join(args)
                info = self.get_video_info_from_keyword(keyword)
            return info
        except:
            return None
    
    
    def get_video_info_from_url(self, url):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
        

    def get_video_info_from_keyword(self, keyword):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            result = ydl.extract_info(keyword, download=False)
            info = result["entries"][0]
            return info
        
        
    def get_voice_client(self, ctx):
        return discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    
    
    def get_music_info(self, id):
        return self.bot.get_cog("Guild").get_guild_info(id).musicInfo
        
        

def setup(bot):
    bot.add_cog(Music(bot))