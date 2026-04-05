import discord
from discord.ext import commands


class SharedMM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.api.get_plugin_partition(self)
        self._patched = False
        self._original_props = {}

    async def cog_load(self):
        await self.coll.update_one(
            {"_id": "config"},
            {
                "$setOnInsert": {
                    "enabled": False,
                    "shared_guild_id": None,
                    "default_category_id": None,
                    "category_ids": [],
                    "log_channel_id": None,
                    "mention_channel_id": None,
                    "update_channel_id": None,
                }
            },
            upsert=True,
        )
        self.patch_bot_properties()

    async def cog_unload(self):
        self.unpatch_bot_properties()

    async def get_config(self):
        data = await self.coll.find_one({"_id": "config"})
        if not data:
            data = {
                "_id": "config",
                "enabled": False,
                "shared_guild_id": None,
                "default_category_id": None,
                "category_ids": [],
                "log_channel_id": None,
                "mention_channel_id": None,
                "update_channel_id": None,
            }
            await self.coll.insert_one(data)
        return data

    async def update_config(self, **kwargs):
        await self.coll.update_one({"_id": "config"}, {"$set": kwargs}, upsert=True)

    def make_embed(self, title, description, color=discord.Color.blurple()):
        return discord.Embed(title=title, description=description, color=color)

    def get_shared_guild_sync(self):
        try:
            cfg = self.coll.database[self.coll.name].find_one({"_id": "config"})
        except Exception:
            return None

        if not cfg or not cfg.get("enabled"):
            return None

        guild_id = cfg.get("shared_guild_id")
        if not guild_id:
            return None

        try:
            return self.bot.get_guild(int(guild_id))
        except Exception:
            return None

    def get_default_category_sync(self):
        guild = self.get_shared_guild_sync()
        if guild is None:
            return None

        try:
            cfg = self.coll.database[self.coll.name].find_one({"_id": "config"})
        except Exception:
            return None

        if not cfg or not cfg.get("enabled"):
            return None

        cat_id = cfg.get("default_category_id")
        if not cat_id:
            return None

        try:
            category = guild.get_channel(int(cat_id))
        except Exception:
            return None

        if isinstance(category, discord.CategoryChannel):
            return category
        return None

    def get_log_channel_sync(self):
        guild = self.get_shared_guild_sync()
        if guild is None:
            return None

        try:
            cfg = self.coll.database[self.coll.name].find_one({"_id": "config"})
        except Exception:
            return None

        if not cfg or not cfg.get("enabled"):
            return None

        channel_id = cfg.get("log_channel_id")
        if not channel_id:
            return None

        try:
            channel = guild.get_channel(int(channel_id))
        except Exception:
            return None

        if isinstance(channel, discord.TextChannel):
            return channel
        return None

    def get_mention_channel_sync(self):
        guild = self.get_shared_guild_sync()
        if guild is None:
            return None

        try:
            cfg = self.coll.database[self.coll.name].find_one({"_id": "config"})
        except Exception:
            return None

        if not cfg or not cfg.get("enabled"):
            return None

        channel_id = cfg.get("mention_channel_id")
        if not channel_id:
            return None

        try:
            channel = guild.get_channel(int(channel_id))
        except Exception:
            return None

        if isinstance(channel, discord.TextChannel):
            return channel
        return None

    def get_update_channel_sync(self):
        guild = self.get_shared_guild_sync()
        if guild is None:
            return None

        try:
            cfg = self.coll.database[self.coll.name].find_one({"_id": "config"})
        except Exception:
            return None

        if not cfg or not cfg.get("enabled"):
            return None

        channel_id = cfg.get("update_channel_id")
        if not channel_id:
            return None

        try:
            channel = guild.get_channel(int(channel_id))
        except Exception:
            return None

        if isinstance(channel, discord.TextChannel):
            return channel
        return None

    def patch_bot_properties(self):
        if self._patched:
            return

        bot_cls = self.bot.__class__

        if hasattr(bot_cls, "modmail_guild"):
            self._original_props["modmail_guild"] = bot_cls.modmail_guild

            def patched_modmail_guild(instance):
                plugin = instance.get_cog("SharedMM")
                if plugin:
                    shared = plugin.get_shared_guild_sync()
                    if shared is not None:
                        return shared
                original = plugin._original_props.get("modmail_guild") if plugin else None
                if original is not None:
                    return original.fget(instance)
                return None

            setattr(bot_cls, "modmail_guild", property(patched_modmail_guild))

        if hasattr(bot_cls, "main_category"):
            self._original_props["main_category"] = bot_cls.main_category

            def patched_main_category(instance):
                plugin = instance.get_cog("SharedMM")
                if plugin:
                    category = plugin.get_default_category_sync()
                    if category is not None:
                        return category
                original = plugin._original_props.get("main_category") if plugin else None
                if original is not None:
                    return original.fget(instance)
                return None

            setattr(bot_cls, "main_category", property(patched_main_category))

        if hasattr(bot_cls, "log_channel"):
            self._original_props["log_channel"] = bot_cls.log_channel

            def patched_log_channel(instance):
                plugin = instance.get_cog("SharedMM")
                if plugin:
                    ch = plugin.get_log_channel_sync()
                    if ch is not None:
                        return ch
                original = plugin._original_props.get("log_channel") if plugin else None
                if original is not None:
                    return original.fget(instance)
                return None

            setattr(bot_cls, "log_channel", property(patched_log_channel))

        if hasattr(bot_cls, "mention_channel"):
            self._original_props["mention_channel"] = bot_cls.mention_channel

            def patched_mention_channel(instance):
                plugin = instance.get_cog("SharedMM")
                if plugin:
                    ch = plugin.get_mention_channel_sync()
                    if ch is not None:
                        return ch
                original = plugin._original_props.get("mention_channel") if plugin else None
                if original is not None:
                    return original.fget(instance)
                return None

            setattr(bot_cls, "mention_channel", property(patched_mention_channel))

        if hasattr(bot_cls, "update_channel"):
            self._original_props["update_channel"] = bot_cls.update_channel

            def patched_update_channel(instance):
                plugin = instance.get_cog("SharedMM")
                if plugin:
                    ch = plugin.get_update_channel_sync()
                    if ch is not None:
                        return ch
                original = plugin._original_props.get("update_channel") if plugin else None
                if original is not None:
                    return original.fget(instance)
                return None

            setattr(bot_cls, "update_channel", property(patched_update_channel))

        self._patched = True

    def unpatch_bot_properties(self):
        if not self._patched:
            return

        bot_cls = self.bot.__class__

        for name, original in self._original_props.items():
            setattr(bot_cls, name, original)

        self._original_props.clear()
        self._patched = False

    async def resolve_category_lines(self, guild, category_ids):
        lines = []
        for cat_id in category_ids:
            try:
                cat = guild.get_channel(int(cat_id))
            except Exception:
                cat = None
            if isinstance(cat, discord.CategoryChannel):
                lines.append(f"{cat.name} (`{cat.id}`)")
            else:
                lines.append(f"Invalid Category (`{cat_id}`)")
        return lines

    @commands.group(name="sharedmm", invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_group(self, ctx):
        cfg = await self.get_config()

        guild = None
        if cfg.get("shared_guild_id"):
            guild = self.bot.get_guild(int(cfg["shared_guild_id"]))

        guild_text = f"{guild.name} (`{guild.id}`)" if guild else (f"`{cfg.get('shared_guild_id')}`" if cfg.get("shared_guild_id") else "Not set")
        default_cat_text = "Not set"
        if guild and cfg.get("default_category_id"):
            cat = guild.get_channel(int(cfg["default_category_id"]))
            if isinstance(cat, discord.CategoryChannel):
                default_cat_text = f"{cat.name} (`{cat.id}`)"
            else:
                default_cat_text = f"Invalid (`{cfg['default_category_id']}`)"
        elif cfg.get("default_category_id"):
            default_cat_text = f"`{cfg['default_category_id']}`"

        category_lines = []
        if guild:
            category_lines = await self.resolve_category_lines(guild, cfg.get("category_ids", []))
        else:
            category_lines = [f"`{x}`" for x in cfg.get("category_ids", [])]

        embed = discord.Embed(title="SharedMM Settings", color=discord.Color.blurple())
        embed.add_field(name="Enabled", value="Yes" if cfg.get("enabled") else "No", inline=False)
        embed.add_field(name="Shared Staff Guild", value=guild_text, inline=False)
        embed.add_field(name="Default Base Category", value=default_cat_text, inline=False)
        embed.add_field(name="Saved Categories", value="\n".join(category_lines) if category_lines else "None", inline=False)
        embed.add_field(
            name="Commands",
            value=(
                f"`{ctx.prefix}sharedmm enable`\n"
                f"`{ctx.prefix}sharedmm disable`\n"
                f"`{ctx.prefix}sharedmm setguild <guild_id>`\n"
                f"`{ctx.prefix}sharedmm setcategory <category_id>`\n"
                f"`{ctx.prefix}sharedmm addcategory <category_id>`\n"
                f"`{ctx.prefix}sharedmm removecategory <category_id>`\n"
                f"`{ctx.prefix}sharedmm setlog <channel_id>`\n"
                f"`{ctx.prefix}sharedmm setmention <channel_id>`\n"
                f"`{ctx.prefix}sharedmm setupdate <channel_id>`\n"
                f"`{ctx.prefix}sharedmm status`"
            ),
            inline=False,
        )
        await ctx.send(embed=embed)

    @sharedmm_group.command(name="enable")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_enable(self, ctx):
        cfg = await self.get_config()
        if not cfg.get("shared_guild_id") or not cfg.get("default_category_id"):
            return await ctx.send(
                embed=self.make_embed(
                    "Missing Setup",
                    "Set the shared guild and default category first.",
                    discord.Color.red(),
                )
            )

        await self.update_config(enabled=True)
        await ctx.send(embed=self.make_embed("SharedMM Enabled", "This Modmail instance will now use the shared staff server/category override.", discord.Color.green()))

    @sharedmm_group.command(name="disable")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_disable(self, ctx):
        await self.update_config(enabled=False)
        await ctx.send(embed=self.make_embed("SharedMM Disabled", "This Modmail instance will now fall back to its normal core routing.", discord.Color.orange()))

    @sharedmm_group.command(name="setguild")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_setguild(self, ctx, guild_id: int):
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return await ctx.send(embed=self.make_embed("Invalid Guild", "That guild is not available to this bot.", discord.Color.red()))

        await self.update_config(shared_guild_id=guild_id)
        await ctx.send(embed=self.make_embed("Shared Guild Set", f"Shared staff guild set to **{guild.name}** (`{guild.id}`).", discord.Color.green()))

    @sharedmm_group.command(name="setcategory")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_setcategory(self, ctx, category_id: int):
        cfg = await self.get_config()
        guild_id = cfg.get("shared_guild_id")
        if not guild_id:
            return await ctx.send(embed=self.make_embed("Set Guild First", "Use `sharedmm setguild` first.", discord.Color.red()))

        guild = self.bot.get_guild(int(guild_id))
        if guild is None:
            return await ctx.send(embed=self.make_embed("Invalid Shared Guild", "The configured shared guild is not available.", discord.Color.red()))

        category = guild.get_channel(category_id)
        if not isinstance(category, discord.CategoryChannel):
            return await ctx.send(embed=self.make_embed("Invalid Category", "That category does not exist in the shared guild.", discord.Color.red()))

        category_ids = list(cfg.get("category_ids", []))
        if category_id not in category_ids:
            category_ids.append(category_id)

        await self.update_config(default_category_id=category_id, category_ids=category_ids)
        await ctx.send(embed=self.make_embed("Default Category Set", f"Default base category set to **{category.name}** (`{category.id}`).", discord.Color.green()))

    @sharedmm_group.command(name="addcategory")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_addcategory(self, ctx, category_id: int):
        cfg = await self.get_config()
        guild_id = cfg.get("shared_guild_id")
        if not guild_id:
            return await ctx.send(embed=self.make_embed("Set Guild First", "Use `sharedmm setguild` first.", discord.Color.red()))

        guild = self.bot.get_guild(int(guild_id))
        if guild is None:
            return await ctx.send(embed=self.make_embed("Invalid Shared Guild", "The configured shared guild is not available.", discord.Color.red()))

        category = guild.get_channel(category_id)
        if not isinstance(category, discord.CategoryChannel):
            return await ctx.send(embed=self.make_embed("Invalid Category", "That category does not exist in the shared guild.", discord.Color.red()))

        category_ids = list(cfg.get("category_ids", []))
        if category_id in category_ids:
            return await ctx.send(embed=self.make_embed("Already Added", "That category is already saved.", discord.Color.orange()))

        category_ids.append(category_id)
        await self.update_config(category_ids=category_ids)
        await ctx.send(embed=self.make_embed("Category Added", f"Saved **{category.name}** (`{category.id}`) as a valid category.", discord.Color.green()))

    @sharedmm_group.command(name="removecategory")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_removecategory(self, ctx, category_id: int):
        cfg = await self.get_config()
        category_ids = list(cfg.get("category_ids", []))

        if category_id not in category_ids:
            return await ctx.send(embed=self.make_embed("Not Found", "That category is not saved.", discord.Color.orange()))

        category_ids.remove(category_id)
        updates = {"category_ids": category_ids}

        if cfg.get("default_category_id") == category_id:
            updates["default_category_id"] = category_ids[0] if category_ids else None

        await self.update_config(**updates)
        await ctx.send(embed=self.make_embed("Category Removed", f"Removed category `{category_id}` from the saved list.", discord.Color.green()))

    @sharedmm_group.command(name="setlog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_setlog(self, ctx, channel_id: int):
        cfg = await self.get_config()
        guild_id = cfg.get("shared_guild_id")
        if not guild_id:
            return await ctx.send(embed=self.make_embed("Set Guild First", "Use `sharedmm setguild` first.", discord.Color.red()))

        guild = self.bot.get_guild(int(guild_id))
        if guild is None:
            return await ctx.send(embed=self.make_embed("Invalid Shared Guild", "The configured shared guild is not available.", discord.Color.red()))

        channel = guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            return await ctx.send(embed=self.make_embed("Invalid Channel", "That text channel does not exist in the shared guild.", discord.Color.red()))

        await self.update_config(log_channel_id=channel_id)
        await ctx.send(embed=self.make_embed("Log Channel Set", f"Log channel set to {channel.mention}.", discord.Color.green()))

    @sharedmm_group.command(name="setmention")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_setmention(self, ctx, channel_id: int):
        cfg = await self.get_config()
        guild_id = cfg.get("shared_guild_id")
        if not guild_id:
            return await ctx.send(embed=self.make_embed("Set Guild First", "Use `sharedmm setguild` first.", discord.Color.red()))

        guild = self.bot.get_guild(int(guild_id))
        if guild is None:
            return await ctx.send(embed=self.make_embed("Invalid Shared Guild", "The configured shared guild is not available.", discord.Color.red()))

        channel = guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            return await ctx.send(embed=self.make_embed("Invalid Channel", "That text channel does not exist in the shared guild.", discord.Color.red()))

        await self.update_config(mention_channel_id=channel_id)
        await ctx.send(embed=self.make_embed("Mention Channel Set", f"Mention channel set to {channel.mention}.", discord.Color.green()))

    @sharedmm_group.command(name="setupdate")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_setupdate(self, ctx, channel_id: int):
        cfg = await self.get_config()
        guild_id = cfg.get("shared_guild_id")
        if not guild_id:
            return await ctx.send(embed=self.make_embed("Set Guild First", "Use `sharedmm setguild` first.", discord.Color.red()))

        guild = self.bot.get_guild(int(guild_id))
        if guild is None:
            return await ctx.send(embed=self.make_embed("Invalid Shared Guild", "The configured shared guild is not available.", discord.Color.red()))

        channel = guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            return await ctx.send(embed=self.make_embed("Invalid Channel", "That text channel does not exist in the shared guild.", discord.Color.red()))

        await self.update_config(update_channel_id=channel_id)
        await ctx.send(embed=self.make_embed("Update Channel Set", f"Update channel set to {channel.mention}.", discord.Color.green()))

    @sharedmm_group.command(name="status")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sharedmm_status(self, ctx):
        cfg = await self.get_config()

        checks = []
        checks.append(f"Enabled: {'Yes' if cfg.get('enabled') else 'No'}")

        shared = self.bot.get_guild(int(cfg["shared_guild_id"])) if cfg.get("shared_guild_id") else None
        checks.append(f"Shared Guild: {'OK' if shared else 'Missing'}")

        default_cat = None
        if shared and cfg.get("default_category_id"):
            default_cat = shared.get_channel(int(cfg["default_category_id"]))
        checks.append(f"Default Category: {'OK' if isinstance(default_cat, discord.CategoryChannel) else 'Missing'}")

        log_channel = None
        if shared and cfg.get("log_channel_id"):
            log_channel = shared.get_channel(int(cfg["log_channel_id"]))
        checks.append(f"Log Channel: {'OK' if isinstance(log_channel, discord.TextChannel) else 'Not set / invalid'}")

        embed = discord.Embed(title="SharedMM Status", description="\n".join(checks), color=discord.Color.blurple())
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_ready(self, thread, creator, category, initial_message):
        cfg = await self.get_config()
        if not cfg.get("enabled"):
            return

        desired_category = self.get_default_category_sync()
        if desired_category is None:
            return

        try:
            if isinstance(thread.channel, discord.TextChannel) and thread.channel.category_id != desired_category.id:
                await thread.channel.edit(category=desired_category, reason="SharedMM enforced default category")
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(SharedMM(bot))
