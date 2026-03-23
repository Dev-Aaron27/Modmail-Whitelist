import re
import discord
from discord.ext import commands


class AutoCorrect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.api.get_plugin_partition(self)

        self.word_map = {
            "u": "you",
            "ur": "your",
            "urs": "yours",
            "r": "are",
            "im": "i'm",
            "idk": "I don't know",
            "ik": "I know",
            "thx": "thanks",
            "ty": "thank you",
            "pls": "please",
            "plz": "please",
            "bc": "because",
            "cuz": "because",
            "abt": "about",
            "tho": "though",
            "wont": "won't",
            "cant": "can't",
            "dont": "don't",
            "didnt": "didn't",
            "isnt": "isn't",
            "arent": "aren't",
            "ive": "I've",
            "ill": "I'll",
            "lemme": "let me",
            "gonna": "going to",
            "wanna": "want to",
            "i": "I",
        }

        self.phrase_map = {
            r"\bhi hru\b": "Hi, how are you?",
            r"\bhey hru\b": "Hey, how are you?",
            r"\bhru\b": "how are you",
            r"\bwyd\b": "what are you doing",
            r"\bwyd rn\b": "what are you doing right now",
            r"\bbrb\b": "be right back",
            r"\bgtg\b": "I have to go",
            r"\bgn\b": "good night",
            r"\bgm\b": "good morning",
            r"\blol\b": "that's funny",
            r"\bomg\b": "oh my God",
            r"\bidk\b": "I don't know",
            r"\btbh\b": "to be honest",
            r"\bbtw\b": "by the way",
            r"\bfyi\b": "for your information",
            r"\bnvm\b": "never mind",
            r"\bnp\b": "no problem",
            r"\btysm\b": "thank you so much",
            r"\bily\b": "I love you",
            r"\blmk\b": "let me know",
            r"\bcan u\b": "can you",
            r"\bdo u\b": "do you",
            r"\bare u\b": "are you",
            r"\bwhy u\b": "why are you",
            r"\bhow u\b": "how are you",
            r"\bwhat u\b": "what are you",
        }

    async def cog_load(self):
        await self.coll.update_one(
            {"_id": "config"},
            {"$setOnInsert": {
                "enabled": True,
                "mode": "channels"
            }},
            upsert=True,
        )

    async def get_config(self):
        return await self.coll.find_one({"_id": "config"}) or {"enabled": True, "mode": "channels"}

    async def update_config(self, **kwargs):
        await self.coll.update_one({"_id": "config"}, {"$set": kwargs}, upsert=True)

    def make_embed(self, title, desc, color=discord.Color.blurple()):
        return discord.Embed(title=title, description=desc, color=color)

    def smart_capitalize(self, text):
        text = text.strip()
        if not text:
            return text
        text = text[0].upper() + text[1:]
        text = re.sub(r"([.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
        return text

    def add_punctuation(self, text):
        if text.endswith(("!", "?", ".")):
            return text
        if text.lower().startswith(("how", "what", "why", "when", "where", "who", "are", "is", "can")):
            return text + "?"
        return text + "."

    def autocorrect_text(self, text):
        corrected = text

        for pattern, repl in self.phrase_map.items():
            corrected = re.sub(pattern, repl, corrected, flags=re.IGNORECASE)

        tokens = re.split(r"(\s+)", corrected)
        corrected = "".join([self.word_map.get(t.lower(), t) for t in tokens])

        corrected = re.sub(r"\bi\b", "I", corrected)
        corrected = self.smart_capitalize(corrected)
        corrected = self.add_punctuation(corrected)

        return corrected

    def should_run(self, message, config):
        if message.author.bot:
            return False

        if not config.get("enabled", True):
            return False

        mode = config.get("mode", "channels")

        if mode == "dm":
            return message.guild is None

        if mode == "channels":
            return message.guild is not None

        return True

    @commands.group(name="autocorrect", invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_group(self, ctx):
        config = await self.get_config()

        embed = discord.Embed(title="AutoCorrect Settings", color=discord.Color.blurple())
        embed.add_field(name="Enabled", value=str(config.get("enabled", True)), inline=False)
        embed.add_field(name="Mode", value=config.get("mode", "channels"), inline=False)
        embed.add_field(
            name="Commands",
            value=(
                f"`{ctx.prefix}autocorrect enable`\n"
                f"`{ctx.prefix}autocorrect disable`\n"
                f"`{ctx.prefix}autocorrect channels`\n"
                f"`{ctx.prefix}autocorrect all`\n"
                f"`{ctx.prefix}autocorrect dm`\n"
                f"`{ctx.prefix}autocorrect test <text>`"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @autocorrect_group.command()
    async def enable(self, ctx):
        await self.update_config(enabled=True)
        await ctx.send(embed=self.make_embed("Enabled", "AutoCorrect is now enabled", discord.Color.green()))

    @autocorrect_group.command()
    async def disable(self, ctx):
        await self.update_config(enabled=False)
        await ctx.send(embed=self.make_embed("Disabled", "AutoCorrect is now disabled", discord.Color.orange()))

    @autocorrect_group.command()
    async def channels(self, ctx):
        await self.update_config(mode="channels")
        await ctx.send(embed=self.make_embed("Mode Set", "Now correcting server/thread messages", discord.Color.green()))

    @autocorrect_group.command()
    async def all(self, ctx):
        await self.update_config(mode="all")
        await ctx.send(embed=self.make_embed("Mode Set", "Now correcting all messages", discord.Color.green()))

    @autocorrect_group.command()
    async def dm(self, ctx):
        await self.update_config(mode="dm")
        await ctx.send(embed=self.make_embed("Mode Set", "Now correcting DM messages only", discord.Color.green()))

    @autocorrect_group.command()
    async def test(self, ctx, *, text):
        corrected = self.autocorrect_text(text)
        embed = discord.Embed(title="AutoCorrect Test", color=discord.Color.blurple())
        embed.add_field(name="Original", value=text, inline=False)
        embed.add_field(name="Corrected", value=corrected, inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        config = await self.get_config()

        if not self.should_run(message, config):
            return

        if not message.content.strip():
            return

        corrected = self.autocorrect_text(message.content)

        if corrected == message.content:
            return

        try:
            await message.delete()
        except Exception:
            return

        embed = discord.Embed(
            title="Auto Corrected",
            description=corrected,
            color=discord.Color.blurple()
        )
        embed.set_footer(text=str(message.author))

        try:
            await message.channel.send(embed=embed)
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(AutoCorrect(bot))
