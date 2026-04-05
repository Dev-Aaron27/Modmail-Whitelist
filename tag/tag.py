from core.checks import has_permissions
from core.models import PermissionLevel

class Tagging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.api.get_plugin_partition(self)

    async def cog_load(self):
        await self.coll.update_one(
            {"_id": "config"},
            {
                "$setOnInsert": {
                    "enabled": True,
                    "max_tag_length": 12,
                    "tag_append": "-"
                }
            },
            upsert=True,
        )

    async def get_config(self):
        data = await self.coll.find_one({"_id": "config"})
        if not data:
            data = {
                "_id": "config",
                "enabled": True,
                "max_tag_length": 12,
                "tag_append": "-"
            }
            await self.coll.insert_one(data)
        return data

    async def update_config(self, **kwargs):
        await self.coll.update_one(
            {"_id": "config"},
            {"$set": kwargs},
            upsert=True,
        )

    def make_embed(self, title, description, color=discord.Color.blurple()):
        return discord.Embed(title=title, description=description, color=color)

    def clean_tag(self, text: str, max_length: int) -> str:
        text = text.strip().lower()
        text = re.sub(r"\s+", "-", text)
        text = re.sub(r"[^a-z0-9\-_]", "", text)
        text = re.sub(r"-{2,}", "-", text)
        text = text.strip("-_")
        return text[:max_length]

    def remove_existing_tag(self, channel_name: str, append: str) -> str:
        if append and append in channel_name:
            first, rest = channel_name.split(append, 1)
            if first and re.fullmatch(r"[a-z0-9\-_]+", first):
                return rest.lstrip("-_ ")
        return channel_name

    @commands.group(name="tagging", invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def tagging_group(self, ctx):
        cfg = await self.get_config()

        embed = discord.Embed(title="Tagging Settings", color=discord.Color.blurple())
        embed.add_field(name="Enabled", value="Yes" if cfg.get("enabled", True) else "No", inline=False)
        embed.add_field(name="Max Tag Length", value=str(cfg.get("max_tag_length", 12)), inline=False)
        embed.add_field(name="Tag Append", value=cfg.get("tag_append", "-"), inline=False)
        embed.add_field(
            name="Commands",
            value=(
                f"`{ctx.prefix}tag <text>`\n"
                f"`{ctx.prefix}untag`\n"
                f"`{ctx.prefix}tagappend <text/emoji>`\n"
                f"`{ctx.prefix}tagging enable`\n"
                f"`{ctx.prefix}tagging disable`\n"
                f"`{ctx.prefix}tagging maxlength <number>`"
            ),
            inline=False,
        )
        await ctx.send(embed=embed)

    @tagging_group.command(name="enable")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def tagging_enable(self, ctx):
        await self.update_config(enabled=True)
        await ctx.send(embed=self.make_embed("Tagging Enabled", "Channel tagging is now enabled.", discord.Color.green()))

    @tagging_group.command(name="disable")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def tagging_disable(self, ctx):
        await self.update_config(enabled=False)
        await ctx.send(embed=self.make_embed("Tagging Disabled", "Channel tagging is now disabled.", discord.Color.orange()))

    @tagging_group.command(name="maxlength")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def tagging_maxlength(self, ctx, number: int):
        if number < 1 or number > 30:
            return await ctx.send(embed=self.make_embed("Invalid Length", "Choose a number between 1 and 30.", discord.Color.red()))

        await self.update_config(max_tag_length=number)
        await ctx.send(embed=self.make_embed("Max Length Updated", f"Tag max length is now `{number}`.", discord.Color.green()))

    @commands.command(name="tagappend")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def tagappend_command(self, ctx, *, text: str):
        text = text.strip()
        if not text:
            return await ctx.send(embed=self.make_embed("Invalid Append", "You need to give some text or emoji.", discord.Color.red()))

        if len(text) > 20:
            return await ctx.send(embed=self.make_embed("Too Long", "Keep the tag append under 20 characters.", discord.Color.red()))

        await self.update_config(tag_append=text)
        await ctx.send(embed=self.make_embed("Tag Append Updated", f"New tag append is now:\n`{text}`", discord.Color.green()))

    @commands.command(name="tag")
    @checks.has_permissions(PermissionLevel.SUPPORT)
    async def tag_command(self, ctx, *, text: str = None):
        cfg = await self.get_config()

        if not cfg.get("enabled", True):
            return await ctx.send(embed=self.make_embed("Disabled", "Tagging is currently disabled.", discord.Color.orange()))

        if not text:
            return await ctx.send(embed=self.make_embed("Usage", f"`{ctx.prefix}tag <text>`", discord.Color.red()))

        thread = await self.bot.threads.find(channel=ctx.channel)
        if thread is None:
            return await ctx.send(embed=self.make_embed("Not a Thread", "This command can only be used in a Modmail thread channel.", discord.Color.red()))

        max_length = int(cfg.get("max_tag_length", 12))
        append = str(cfg.get("tag_append", "-"))
        cleaned = self.clean_tag(text, max_length)

        if not cleaned:
            return await ctx.send(embed=self.make_embed("Invalid Tag", "That tag became empty after cleaning. Use letters or numbers.", discord.Color.red()))

        base_name = self.remove_existing_tag(ctx.channel.name, append)
        new_name = f"{cleaned}{append}{base_name}"

        if len(new_name) > 100:
            overflow = len(new_name) - 100
            if overflow >= len(base_name):
                base_name = base_name[:1]
            else:
                base_name = base_name[:-overflow]
            new_name = f"{cleaned}{append}{base_name}"

        try:
            await ctx.channel.edit(name=new_name, reason=f"Thread tagged by {ctx.author}")
        except discord.HTTPException as e:
            return await ctx.send(embed=self.make_embed("Failed", f"Could not rename the channel.\n`{e}`", discord.Color.red()))

        await ctx.send(embed=self.make_embed("Tag Added", f"New channel name:\n`{new_name}`", discord.Color.green()))

    @commands.command(name="untag")
    @checks.has_permissions(PermissionLevel.SUPPORT)
    async def untag_command(self, ctx):
        cfg = await self.get_config()

        if not cfg.get("enabled", True):
            return await ctx.send(embed=self.make_embed("Disabled", "Tagging is currently disabled.", discord.Color.orange()))

        thread = await self.bot.threads.find(channel=ctx.channel)
        if thread is None:
            return await ctx.send(embed=self.make_embed("Not a Thread", "This command can only be used in a Modmail thread channel.", discord.Color.red()))

        append = str(cfg.get("tag_append", "-"))
        current_name = ctx.channel.name
        new_name = self.remove_existing_tag(current_name, append)

        if new_name == current_name:
            return await ctx.send(embed=self.make_embed("No Tag", "This channel does not currently have a tag.", discord.Color.orange()))

        try:
            await ctx.channel.edit(name=new_name, reason=f"Thread untagged by {ctx.author}")
        except discord.HTTPException as e:
            return await ctx.send(embed=self.make_embed("Failed", f"Could not rename the channel.\n`{e}`", discord.Color.red()))

        await ctx.send(embed=self.make_embed("Tag Removed", f"New channel name:\n`{new_name}`", discord.Color.green()))


async def setup(bot):
    await bot.add_cog(Tagging(bot))
