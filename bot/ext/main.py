import disnake as discord
from disnake.ext import commands
import difflib
import psutil
from datetime import datetime

def get_command_info(cmd):
    if isinstance(cmd, commands.InvokableSlashCommand):
        return cmd.name, cmd.description
    elif isinstance(cmd, commands.SubCommand):
        return cmd.qualified_name, cmd.option.description

not_added = commands.BadArgument("This channel has not been added yet")
no_added = commands.BadArgument("You haven't added any channels yet")

@commands.slash_command(name="voice")
@commands.bot_has_guild_permissions(manage_channels=True)
async def parent(_):
    """Controls behaviour of the voice channels"""
    pass

@parent.sub_command(name="name")
async def child_name(ctx, name: str):
    """Changes the name of your current voice channel"""
    if ctx.author.voice is None:
        raise commands.BadArgument("You must be in a voice channel")
    await ctx.author.voice.channel.edit(name=name)
    await ctx.send(f"Changed name to `{name}`")

#change the limit of your current voice channel
@parent.sub_command(name="limit")
async def child_limit(ctx, limit: int = commands.Param(min_value=0, max_value=99)):
    """Changes the userlimit of your current voice channel"""
    if ctx.author.voice is None:
        raise commands.BadArgument("You must be in a voice channel")
    await ctx.author.voice.channel.edit(user_limit=limit)
    await ctx.send(f"Changed limit to `{limit}`")

def setup(bot):
    bot.add_slash_command(parent)
