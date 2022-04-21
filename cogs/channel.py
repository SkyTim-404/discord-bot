import discord
from discord.ext import commands

class Channel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel")
            return
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)
            
            
    @commands.command(aliases = ["dc", "leave"])
    async def disconnect(self, ctx):
        self.bot.get_cog("Guild").get_guild_info(ctx.guild.id).clear_music_info()
        if ctx.voice_client is None:
            await ctx.send("Bot is not in a voice channel")
            return
        await ctx.voice_client.disconnect()
        
        
        
def setup(bot):
    bot.add_cog(Channel(bot))