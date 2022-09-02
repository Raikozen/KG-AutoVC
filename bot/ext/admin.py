import disnake as discord
from disnake.ext import commands
import psutil
from datetime import datetime

permissions = discord.Permissions(
    manage_channels=True,  # for creating/deleting/moving channels
    move_members=True,  # for moving members into new channels
    connect=True,  # required for deleting channels, see Forbidden: Missing Access
    manage_roles=True  # required for setting channel permissions
)

class Default(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def configure(self, channel, key, value):
        try:
            self.bot.configs[str(channel.id)][key] = value
        except KeyError:
            raise commands.BadArgument("This channel has not been added yet")
        else:
            await self.bot.configs.save()

    # INITIAL SETUP FOR ADMIN COMMANDS
    @commands.slash_command(name="vcadmin")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.has_role("VoiceAdmin")
    async def parent(self, _):
        """Default settings for created channels"""
        pass

    # SETTING UP THE PARENT CHANNEL
    @parent.sub_command(name="setup")
    @commands.bot_has_guild_permissions(move_members=True, manage_roles=True, connect=True)
    async def child_setup(ctx):
        """Automatically creates a new category, a starter channel and adds it to the starter list"""
        category = await ctx.guild.create_category("Voice Channels")
        channel = await category.create_voice_channel("➕ Click to create VC")
        ctx.bot.configs[str(channel.id)] = {}
        await ctx.bot.configs.save()
        await ctx.send(f"A new category and a new starter channel have been created. Join `{channel.name}` and try it out")

    # SETUP THE DEFAULT NAME FOR THE CHANNELS
    @parent.sub_command(name="defaultname")
    async def child_name(self, ctx, channel: discord.VoiceChannel, name: str):
        """Sets the default name of a voice channel."""
        await self.configure(channel, "name", name)
        await ctx.send(f"Default name has been set to `{name}`")

    # ADD NEW CHANNEL TO THE STARTER LIST
    @parent.sub_command(name="addchannel")
    async def child_add(self, ctx, channel: discord.VoiceChannel):
        """Adds a channel to the starter list"""
        if str(channel.id) in self.bot.configs:
            raise commands.BadArgument("This channel has already been added")
        self.bot.configs[str(channel.id)] = {}
        await self.bot.configs.save()
        await ctx.send(f"Channel `{channel.name}` has been added to the starter channels")

    # SET THE DEFAULT USERLIMIT ON A CHANNEL
    @parent.sub_command(name="defaultlimit")
    async def child_limit(self, ctx, channel: discord.VoiceChannel, limit: int = commands.Param(min_value=0, max_value=99)):
        """Sets the default userlimit of a voice channel."""
        await self.configure(channel, "limit", limit)
        await ctx.send(f"Default limit has been set to `{limit}`")

    # SET THE DEFAULT BITRATE ON A CHANNEL
    @parent.sub_command(name="defaultbitrate")
    async def child_bitrate(self, ctx, channel: discord.VoiceChannel, bitrate: int = commands.Param(min_value=8000, max_value=384000)):
        """Sets the default bitrate of a voice channel."""
        limit = int(channel.guild.bitrate_limit)
        if bitrate > limit:
            raise commands.BadArgument(f"Bitrate cannot be higher than {limit}")
        await self.configure(channel, "bitrate", bitrate)
        await ctx.send(f"Default bitrate has been set to `{bitrate}`")

    # LISTS ALL CHANNELS INCLUDING THEIR SETTINGS
    @parent.sub_command(name="list")
    async def child_list(ctx):
        """Lists all voice channels including their settings"""
        channels = [c for c in ctx.guild.voice_channels if str(c.id) in ctx.bot.configs]
        if len(channels) == 0:
            raise no_added
        else:
            embed = discord.Embed(
                title="KG Voice Channels",
                description="Here is a list with all voice channels in this server:",
                color=discord.Color.blue()
            )
            for channel in channels:
                settings = ctx.bot.get_settings(channel)
                category = ctx.guild.get_channel(settings["category"])
                embed.add_field(
                    name=f"{channel.name} (ID: {channel.id})",
                    value=f"Category: `{'no category' if category is None else category.name}`\n"
                        f"Name: `{settings['name']}`\n"
                        f"Limit: `{settings['limit']} users`\n" 
                        f"Bitrate: `{settings['bitrate']} kbps`\n"
                        f"Position: `{settings['position']}`",
                    inline=False
                )
            await ctx.send(embed=embed)

    # SHOWS BASIC BOT INFORMATION
    @parent.sub_command(name="info")
    async def child_info(ctx):
        """Shows you information about the bot"""
        embed = discord.Embed(color=ctx.guild.me.color)
        embed.set_thumbnail(url=ctx.bot.user.avatar.url)
        owner = await ctx.bot.get_owner()
        embed.set_author(name=f'Developer: {owner}', icon_url=owner.avatar.url)
        proc = psutil.Process()
        with proc.oneshot():
            uptime = datetime.utcnow() - ctx.bot.launched_at
            mem_total = psutil.virtual_memory().total / (1024 ** 2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)
            cpu_usage = proc.cpu_percent() / psutil.cpu_count()
        embed.add_field(name="Servers", value=str(len(ctx.bot.guilds)))
        embed.add_field(name="Channels", value=str(len(ctx.bot.channels)))
        embed.add_field(name="Latency", value=f"{round(ctx.bot.latency * 1000, 2)} ms")
        embed.add_field(name="Uptime", value=str(uptime))
        embed.add_field(name="CPU usage", value=f"{round(cpu_usage)}%")
        embed.add_field(name="Memory usage", value=f"{int(mem_usage)} / {int(mem_total)} MiB ({round(mem_of_total)}%)")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Default(bot))
