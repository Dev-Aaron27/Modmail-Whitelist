import discord
from discord.ext import commands


class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.api.get_plugin_partition(self)

    async def cog_load(self):
        await self.coll.update_one(
            {"_id": "config"},
            {
                "$setOnInsert": {
                    "enabled": False,
                    "role_ids": [],
                    "deny_message": "You cannot open Modmail right now.\nYou need one of the required server roles first."
                }
            },
            upsert=True,
        )

    async def get_config(self):
        data = await self.coll.find_one({"_id": "config"})
        if not data:
            data = {
                "_id": "config",
                "enabled": False,
                "role_ids": [],
                "deny_message": "You cannot open Modmail right now.\nYou need one of the required server roles first."
            }
            await self.coll.insert_one(data)
        return data

    async def update_config(self, **kwargs):
        await self.coll.update_one(
            {"_id": "config"},
            {"$set": kwargs},
            upsert=True,
        )

    def get_main_guild(self):
        guild = getattr(self.bot, "guild", None)
        if isinstance(guild, discord.Guild):
            return guild

        guild_id = getattr(self.bot, "guild_id", None)
        if isinstance(guild_id, int):
            found = self.bot.get_guild(guild_id)
            if found:
                return found

        main_guild = getattr(self.bot, "main_guild", None)
        if isinstance(main_guild, discord.Guild):
            return main_guild

        if isinstance(main_guild, int):
            found = self.bot.get_guild(main_guild)
            if found:
                return found

        if len(self.bot.guilds) == 1:
            return self.bot.guilds[0]

        return None

    async def member_has_whitelist_role(self, user, role_ids):
        guild = self.get_main_guild()
        if guild is None:
            return False

        member = guild.get_member(user.id)
        if member is None:
            try:
                member = await guild.fetch_member(user.id)
            except Exception:
                return False

        member_role_ids = {role.id for role in member.roles}
        return any(role_id in member_role_ids for role_id in role_ids)

    async def is_allowed(self, user):
        config = await self.get_config()

        if not config.get("enabled", False):
            return True

        role_ids = config.get("role_ids", [])
        if not role_ids:
            return False

        return await self.member_has_whitelist_role(user, role_ids)

    async def send_deny_message(self, user):
        config = await self.get_config()
        embed = discord.Embed(
            title="Modmail Access Denied",
            description=config.get("deny_message", "You are not allowed to use Modmail."),
            color=discord.Color.red()
        )
        try:
            await user.send(embed=embed)
        except Exception:
            pass

    def make_embed(self, title, description, color=discord.Color.blurple()):
        return discord.Embed(title=title, description=description, color=color)

    @commands.group(name="whitelist", invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist_group(self, ctx):
        config = await self.get_config()
        role_ids = config.get("role_ids", [])

        role_mentions = []
        for role_id in role_ids:
            role = ctx.guild.get_role(role_id)
            role_mentions.append(role.mention if role else f"`{role_id}`")

        status = "Enabled" if config.get("enabled", False) else "Disabled"
        roles_text = "\n".join(role_mentions) if role_mentions else "None set"
        deny_message = config.get("deny_message", "Not set")

        embed = discord.Embed(title="Whitelist Settings", color=discord.Color.blurple())
        embed.add_field(name="Status", value=status, inline=False)
        embed.add_field(name="Roles", value=roles_text, inline=False)
        embed.add_field(name="Deny Message", value=deny_message[:1024], inline=False)
        embed.add_field(
            name="Commands",
            value=(
                f"`{ctx.prefix}whitelist enable`\n"
                f"`{ctx.prefix}whitelist disable`\n"
                f"`{ctx.prefix}whitelist dissable`\n"
                f"`{ctx.prefix}whitelist add <role_id>`\n"
                f"`{ctx.prefix}whitelist remove <role_id>`\n"
                f"`{ctx.prefix}whitelist message <text>`\n"
                f"`{ctx.prefix}whitelist list`"
            ),
            inline=False,
        )
        await ctx.send(embed=embed)

    @whitelist_group.command(name="enable")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist_enable(self, ctx):
        await self.update_config(enabled=True)
        await ctx.send(embed=self.make_embed("Whitelist Enabled", "Users will now need a whitelisted role to DM Modmail.", discord.Color.green()))

    @whitelist_group.command(name="disable")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist_disable(self, ctx):
        await self.update_config(enabled=False)
        await ctx.send(embed=self.make_embed("Whitelist Disabled", "Users can now DM Modmail without a whitelist role.", discord.Color.orange()))

    @whitelist_group.command(name="dissable")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist_dissable(self, ctx):
        await self.update_config(enabled=False)
        await ctx.send(embed=self.make_embed("Whitelist Disabled", "Users can now DM Modmail without a whitelist role.", discord.Color.orange()))

    @whitelist_group.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist_add(self, ctx, role_id: int):
        config = await self.get_config()
        role_ids = config.get("role_ids", [])

        if role_id in role_ids:
            return await ctx.send(embed=self.make_embed("Role Already Added", "That role is already in the whitelist.", discord.Color.orange()))

        role = ctx.guild.get_role(role_id)
        if role is None:
            return await ctx.send(embed=self.make_embed("Invalid Role", "That role ID does not exist in this server.", discord.Color.red()))

        role_ids.append(role_id)
        await self.update_config(role_ids=role_ids)
        await ctx.send(embed=self.make_embed("Role Added", f"{role.mention} has been added to the whitelist.", discord.Color.green()))

    @whitelist_group.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist_remove(self, ctx, role_id: int):
        config = await self.get_config()
        role_ids = config.get("role_ids", [])

        if role_id not in role_ids:
            return await ctx.send(embed=self.make_embed("Role Not Found", "That role is not in the whitelist.", discord.Color.orange()))

        role_ids.remove(role_id)
        await self.update_config(role_ids=role_ids)

        role = ctx.guild.get_role(role_id)
        role_text = role.mention if role else f"`{role_id}`"
        await ctx.send(embed=self.make_embed("Role Removed", f"{role_text} has been removed from the whitelist.", discord.Color.green()))

    @whitelist_group.command(name="list")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist_list(self, ctx):
        config = await self.get_config()
        role_ids = config.get("role_ids", [])

        if not role_ids:
            return await ctx.send(embed=self.make_embed("Whitelist Roles", "No whitelist roles have been set.", discord.Color.orange()))

        formatted = []
        for role_id in role_ids:
            role = ctx.guild.get_role(role_id)
            formatted.append(role.mention if role else f"`{role_id}`")

        embed = discord.Embed(title="Whitelist Roles", description="\n".join(formatted), color=discord.Color.blurple())
        await ctx.send(embed=embed)

    @whitelist_group.command(name="message", aliases=["setmessage", "denymsg", "denymessage"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist_message(self, ctx, *, message: str):
        if len(message) > 1900:
            return await ctx.send(embed=self.make_embed("Message Too Long", "Keep the deny message under 1900 characters.", discord.Color.red()))

        await self.update_config(deny_message=message)
        await ctx.send(embed=self.make_embed("Deny Message Updated", message, discord.Color.green()))

    @commands.Cog.listener()
    async def on_thread_initiate(self, thread, creator, category, initial_message):
        allowed = await self.is_allowed(creator)
        if allowed:
            return

        await self.send_deny_message(creator)

        close = getattr(thread, "close", None)
        if callable(close):
            try:
                await close(
                    closer=self.bot.user,
                    silent=True,
                    delete_channel=True,
                    message="User failed whitelist check."
                )
                return
            except TypeError:
                try:
                    await close(
                        closer=self.bot.user,
                        message="User failed whitelist check."
                    )
                    return
                except Exception:
                    pass
            except Exception:
                pass

        channel = getattr(thread, "channel", None)
        if isinstance(channel, discord.TextChannel):
            try:
                embed = discord.Embed(
                    title="Whitelist Blocked",
                    description="This thread was closed because the user does not have a whitelisted role.",
                    color=discord.Color.red()
                )
                await channel.send(embed=embed)
            except Exception:
                pass
            try:
                await channel.delete(reason="User failed whitelist role check.")
            except Exception:
                pass


async def setup(bot):
    await bot.add_cog(Whitelist(bot))
