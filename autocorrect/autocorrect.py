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
            "im": "I'm",
            "idk": "I don't know",
            "ik": "I know",
            "thx": "thanks",
            "ty": "thank you",
            "tysm": "thank you so much",
            "pls": "please",
            "pls.": "please.",
            "plz": "please",
            "bc": "because",
            "cuz": "because",
            "coz": "because",
            "abt": "about",
            "tho": "though",
            "wont": "won't",
            "cant": "can't",
            "dont": "don't",
            "didnt": "didn't",
            "doesnt": "doesn't",
            "isnt": "isn't",
            "arent": "aren't",
            "wasnt": "wasn't",
            "werent": "weren't",
            "hasnt": "hasn't",
            "havent": "haven't",
            "hadnt": "hadn't",
            "wouldnt": "wouldn't",
            "couldnt": "couldn't",
            "shouldnt": "shouldn't",
            "ill": "I'll",
            "ive": "I've",
            "id": "I'd",
            "lemme": "let me",
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "got to",
            "kinda": "kind of",
            "sorta": "sort of",
            "rn": "right now",
            "tmr": "tomorrow",
            "tmrw": "tomorrow",
            "smth": "something",
            "nvm": "never mind",
            "np": "no problem",
            "yw": "you're welcome",
            "ily": "I love you",
            "ilysm": "I love you so much",
            "wyd": "what are you doing",
            "hru": "how are you",
            "wb": "welcome back",
            "brb": "be right back",
            "afk": "away from keyboard",
            "lmk": "let me know",
            "asap": "as soon as possible",
            "fyi": "for your information",
            "imo": "in my opinion",
            "imo": "in my opinion",
            "tbh": "to be honest",
            "btw": "by the way",
            "irl": "in real life",
            "fr": "for real",
            "ngl": "not going to lie",
            "wya": "where are you at",
            "yh": "yeah",
            "ye": "yeah",
            "yhh": "yeah",
            "nah": "no",
            "nope": "no",
            "yep": "yes",
            "yea": "yeah",
            "msg": "message",
            "dm": "direct message",
            "acc": "account",
            "prob": "problem",
            "vid": "video",
            "pic": "picture",
            "ppl": "people",
            "fav": "favorite",
            "sec": "second",
            "mins": "minutes",
            "min": "minute",
            "info": "information",
            "bcs": "because",
            "alr": "alright",
            "tho?": "though?",
            "tho.": "though.",
            "ok": "okay",
            "oky": "okay",
            "kk": "okay",
            "mk": "okay",
            "omw": "on my way",
            "atm": "at the moment",
            "ttyl": "talk to you later",
            "gtg": "I have to go",
            "gn": "good night",
            "gm": "good morning",
            "ge": "good evening",
            "bro": "bro",
            "cus": "because",
            "bcs": "because",
            "thru": "through",
            "wiv": "with",
            "som1": "someone",
            "sum1": "someone",
            "any1": "anyone",
            "every1": "everyone",
            "thoh": "though",
            "teh": "the",
            "adn": "and",
            "wiht": "with",
            "recieve": "receive",
            "seperate": "separate",
            "definately": "definitely",
            "enviroment": "environment",
            "occured": "occurred",
            "untill": "until",
            "becuase": "because",
            "agian": "again",
            "wierd": "weird",
            "agianst": "against",
            "mesage": "message",
            "messege": "message",
            "emebd": "embed",
            "emebds": "embeds",
            "permision": "permission",
            "permisions": "permissions",
            "roleid": "role ID",
            "cahr": "char",
            "charageter": "character",
            "dissable": "disable",
            "enabe": "enable",
            "custon": "custom",
            "modmial": "modmail",
            "plguin": "plugin",
            "whgar": "what",
            "curerent": "current",
            "foinf": "going",
            "tro": "to",
            "techenicaly": "technically",
            "premum": "premium",
            "acces": "access",
            "accses": "access",
            "wqork": "work",
            "rgohjt": "right",
            "fu lk": "full",
            "fukl": "full",
        }

        self.phrase_map = {
            r"\bhi hru\b": "Hi, how are you",
            r"\bhey hru\b": "Hey, how are you",
            r"\bhello hru\b": "Hello, how are you",
            r"\bhi wyd\b": "Hi, what are you doing",
            r"\bhey wyd\b": "Hey, what are you doing",
            r"\bcan u\b": "can you",
            r"\bcould u\b": "could you",
            r"\bwould u\b": "would you",
            r"\bdo u\b": "do you",
            r"\bdid u\b": "did you",
            r"\bare u\b": "are you",
            r"\bwere u\b": "were you",
            r"\bwill u\b": "will you",
            r"\bhave u\b": "have you",
            r"\bhow r u\b": "how are you",
            r"\bhow r ya\b": "how are you",
            r"\bwhere r u\b": "where are you",
            r"\bwhat r u doing\b": "what are you doing",
            r"\bwhy r u\b": "why are you",
            r"\bwhen r u\b": "when are you",
            r"\bwho r u\b": "who are you",
            r"\bi cant\b": "I can't",
            r"\bi wont\b": "I won't",
            r"\bi dont\b": "I don't",
            r"\bi didnt\b": "I didn't",
            r"\bi wasnt\b": "I wasn't",
            r"\bi werent\b": "I weren't",
            r"\bi havent\b": "I haven't",
            r"\bi shouldnt\b": "I shouldn't",
            r"\bi couldnt\b": "I couldn't",
            r"\bi wouldnt\b": "I wouldn't",
            r"\bhelp me pls\b": "please help me",
            r"\bpls help\b": "please help",
            r"\bcan you help me pls\b": "can you help me please",
            r"\bcan u help me\b": "can you help me",
            r"\bcan u help\b": "can you help",
            r"\bi need help pls\b": "I need help please",
            r"\bi need help\b": "I need help",
            r"\bwhat do u mean\b": "what do you mean",
            r"\bwhat do u think\b": "what do you think",
            r"\bwhy did u\b": "why did you",
            r"\bwhen did u\b": "when did you",
            r"\bwhere did u\b": "where did you",
            r"\bthank u\b": "thank you",
            r"\bty for\b": "thank you for",
            r"\bsend me ur\b": "send me your",
            r"\bgive me ur\b": "give me your",
            r"\bmsg me\b": "message me",
            r"\bdm me\b": "direct message me",
            r"\blmk if\b": "let me know if",
            r"\blmk when\b": "let me know when",
            r"\bbrb\b": "be right back",
            r"\bbtw\b": "by the way",
            r"\bfyi\b": "for your information",
            r"\btbh\b": "to be honest",
            r"\bimo\b": "in my opinion",
            r"\bafaik\b": "as far as I know",
            r"\basap\b": "as soon as possible",
            r"\bomg\b": "oh my God",
            r"\bwtf\b": "what the hell",
            r"\bwyd rn\b": "what are you doing right now",
            r"\bhru rn\b": "how are you right now",
            r"\bi love u\b": "I love you",
            r"\bi miss u\b": "I miss you",
            r"\bare u okay\b": "are you okay",
            r"\bu okay\b": "are you okay",
            r"\bu there\b": "are you there",
            r"\br u there\b": "are you there",
            r"\br u okay\b": "are you okay",
            r"\bi gotta go\b": "I have to go",
            r"\bi gtg\b": "I have to go",
            r"\bgood mornin\b": "good morning",
            r"\bgood nite\b": "good night",
            r"\bhows it going\b": "how is it going",
            r"\bhows ur day\b": "how is your day",
            r"\bhows your day\b": "how is your day",
            r"\bi dunno\b": "I don't know",
            r"\bidk what to do\b": "I don't know what to do",
            r"\bive got\b": "I've got",
            r"\bill do it\b": "I'll do it",
            r"\bive done it\b": "I've done it",
            r"\bive fixed it\b": "I've fixed it",
            r"\bive tried\b": "I've tried",
            r"\bive sent\b": "I've sent",
            r"\bive made\b": "I've made",
            r"\bive been\b": "I've been",
        }

    async def cog_load(self):
        await self.coll.update_one(
            {"_id": "config"},
            {
                "$setOnInsert": {
                    "enabled": True,
                    "mode": "channels"
                }
            },
            upsert=True,
        )

    async def get_config(self):
        data = await self.coll.find_one({"_id": "config"})
        if not data:
            data = {"_id": "config", "enabled": True, "mode": "channels"}
            await self.coll.insert_one(data)
        return data

    async def update_config(self, **kwargs):
        await self.coll.update_one({"_id": "config"}, {"$set": kwargs}, upsert=True)

    def make_embed(self, title, description, color=discord.Color.blurple()):
        return discord.Embed(title=title, description=description, color=color)

    async def get_prefixes(self, message):
        prefixes = []

        bot_prefix = getattr(self.bot, "command_prefix", None)

        if callable(bot_prefix):
            try:
                value = bot_prefix(self.bot, message)
                if hasattr(value, "__await__"):
                    value = await value
                if isinstance(value, str):
                    prefixes.append(value)
                elif isinstance(value, (list, tuple, set)):
                    prefixes.extend([p for p in value if isinstance(p, str)])
            except Exception:
                pass
        elif isinstance(bot_prefix, str):
            prefixes.append(bot_prefix)
        elif isinstance(bot_prefix, (list, tuple, set)):
            prefixes.extend([p for p in bot_prefix if isinstance(p, str)])

        config = getattr(self.bot, "config", None)
        if config:
            for key in ("prefix", "command_prefix"):
                try:
                    value = getattr(config, key, None)
                    if isinstance(value, str) and value not in prefixes:
                        prefixes.append(value)
                except Exception:
                    pass
                try:
                    value = config.get(key)
                    if isinstance(value, str) and value not in prefixes:
                        prefixes.append(value)
                except Exception:
                    pass

        try:
            value = getattr(self.bot, "prefix", None)
            if isinstance(value, str) and value not in prefixes:
                prefixes.append(value)
        except Exception:
            pass

        defaults = ["?", ".", "!"]
        for p in defaults:
            if p not in prefixes:
                prefixes.append(p)

        clean = []
        seen = set()
        for p in prefixes:
            if not p:
                continue
            if p in seen:
                continue
            seen.add(p)
            clean.append(p)

        clean.sort(key=len, reverse=True)
        return clean

    def should_run(self, message, config):
        if message.author.bot:
            return False

        if message.webhook_id is not None:
            return False

        if message.embeds:
            return False

        if not message.content or not message.content.strip():
            return False

        if not config.get("enabled", True):
            return False

        mode = config.get("mode", "channels")

        if mode == "dm":
            return message.guild is None

        if mode == "channels":
            return message.guild is not None

        return True

    def fix_tokens(self, text):
        parts = re.split(r"(\s+)", text)
        new_parts = []

        for part in parts:
            key = part.lower()
            replacement = self.word_map.get(key)
            if replacement is not None:
                new_parts.append(replacement)
            else:
                new_parts.append(part)

        return "".join(new_parts)

    def fix_common_patterns(self, text):
        text = re.sub(r"\bim\b", "I'm", text, flags=re.IGNORECASE)
        text = re.sub(r"\bive\b", "I've", text, flags=re.IGNORECASE)
        text = re.sub(r"\bill\b", "I'll", text, flags=re.IGNORECASE)
        text = re.sub(r"\bid\b", "I'd", text, flags=re.IGNORECASE)
        text = re.sub(r"\bi\b", "I", text)
        text = re.sub(r"\s+([,.!?])", r"\1", text)
        text = re.sub(r"([,.!?])([A-Za-z])", r"\1 \2", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"\b(i am)\b", "I am", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(i have)\b", "I have", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(i will)\b", "I will", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(i would)\b", "I would", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(can i)\b", "Can I", text, flags=re.IGNORECASE)
        return text.strip()

    def smart_capitalize(self, text):
        if not text:
            return text

        text = text[0].upper() + text[1:]

        def repl(match):
            return match.group(1) + match.group(2).upper()

        text = re.sub(r"([.!?]\s+)([a-z])", repl, text)
        return text

    def add_punctuation(self, text):
        if not text:
            return text

        stripped = text.rstrip()
        if stripped.endswith(("!", "?", ".", "...")):
            return stripped

        lowered = stripped.lower()
        question_starts = (
            "how", "what", "why", "when", "where", "who", "are", "is", "do", "did",
            "does", "can", "could", "would", "will", "have", "has", "had", "should"
        )

        excited_starts = ("hi", "hello", "hey", "thanks", "thank you")

        if lowered.startswith(question_starts):
            return stripped + "?"
        if lowered.startswith(excited_starts):
            return stripped + "!"
        return stripped + "."

    def autocorrect_text(self, text):
        corrected = text.strip()

        if not corrected:
            return corrected

        for pattern, replacement in self.phrase_map.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

        corrected = self.fix_tokens(corrected)
        corrected = self.fix_common_patterns(corrected)
        corrected = self.smart_capitalize(corrected)
        corrected = self.add_punctuation(corrected)

        corrected = re.sub(r"\bhi,?\s+how are you\b", "Hi, how are you", corrected, flags=re.IGNORECASE)
        corrected = re.sub(r"\bhey,?\s+how are you\b", "Hey, how are you", corrected, flags=re.IGNORECASE)
        corrected = re.sub(r"\bhello,?\s+how are you\b", "Hello, how are you", corrected, flags=re.IGNORECASE)
        corrected = re.sub(r"\bwhat are you doing right now\b", "What are you doing right now", corrected, flags=re.IGNORECASE)
        corrected = re.sub(r"\bi don't know\b", "I don't know", corrected, flags=re.IGNORECASE)
        corrected = re.sub(r"\blet me know\b", "Let me know", corrected, flags=re.IGNORECASE)

        if corrected:
            corrected = corrected[0].upper() + corrected[1:]

        return corrected

    @commands.group(name="autocorrect", invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_group(self, ctx):
        config = await self.get_config()

        embed = discord.Embed(title="AutoCorrect Settings", color=discord.Color.blurple())
        embed.add_field(name="Enabled", value="Yes" if config.get("enabled", True) else "No", inline=False)
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
            inline=False,
        )
        await ctx.send(embed=embed)

    @autocorrect_group.command(name="enable")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_enable(self, ctx):
        await self.update_config(enabled=True)
        await ctx.send(embed=self.make_embed("AutoCorrect Enabled", "AutoCorrect is now enabled.", discord.Color.green()))

    @autocorrect_group.command(name="disable")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_disable(self, ctx):
        await self.update_config(enabled=False)
        await ctx.send(embed=self.make_embed("AutoCorrect Disabled", "AutoCorrect is now disabled.", discord.Color.orange()))

    @autocorrect_group.command(name="channels")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_channels(self, ctx):
        await self.update_config(mode="channels")
        await ctx.send(embed=self.make_embed("Mode Updated", "AutoCorrect will now only run in server and thread channels.", discord.Color.green()))

    @autocorrect_group.command(name="all")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_all(self, ctx):
        await self.update_config(mode="all")
        await ctx.send(embed=self.make_embed("Mode Updated", "AutoCorrect will now run in all supported messages.", discord.Color.green()))

    @autocorrect_group.command(name="dm")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_dm(self, ctx):
        await self.update_config(mode="dm")
        await ctx.send(embed=self.make_embed("Mode Updated", "AutoCorrect will now only run in DMs.", discord.Color.green()))

    @autocorrect_group.command(name="test")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_test(self, ctx, *, text):
        corrected = self.autocorrect_text(text)
        embed = discord.Embed(title="AutoCorrect Test", color=discord.Color.blurple())
        embed.add_field(name="Original", value=text[:1024], inline=False)
        embed.add_field(name="Corrected", value=corrected[:1024], inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        config = await self.get_config()

        if not self.should_run(message, config):
            return

        prefixes = await self.get_prefixes(message)
        content = message.content.strip()

        if any(content.startswith(prefix) for prefix in prefixes):
            return

        corrected = self.autocorrect_text(content)

        if corrected == content:
            return

        try:
            await message.delete()
        except Exception:
            return

        embed = discord.Embed(
            title="Auto Corrected",
            description=corrected[:4096],
            color=discord.Color.blurple()
        )
        embed.set_footer(text=str(message.author))

        try:
            await message.channel.send(embed=embed)
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(AutoCorrect(bot))
