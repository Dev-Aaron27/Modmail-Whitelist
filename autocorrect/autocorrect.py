import re
import inspect
from functools import wraps

import discord
from discord.ext import commands


class AutoCorrect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.api.get_plugin_partition(self)
        self.patched_commands = {}

        self.default_target_commands = [
            "reply",
            "freply",
            "fpreply",
            "fareply",
            "areply",
            "anonreply",
            "ar",
            "r",
            "fr",
            "fpr",
            "far",
            "a",
            "snippet",
            "snippets",
            "s",
        ]

        self.preferred_param_names = {
            "msg",
            "message",
            "text",
            "content",
            "body",
            "reply",
            "response",
            "value",
        }

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
            "plz": "please",
            "bc": "because",
            "cuz": "because",
            "coz": "because",
            "cus": "because",
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
            "charageter": "character",
            "dissable": "disable",
            "enabe": "enable",
            "custon": "custom",
            "modmial": "modmail",
            "plguin": "plugin",
            "curerent": "current",
            "premum": "premium",
            "acces": "access",
            "accses": "access",
            "wqork": "work",
            "rgohjt": "right",
            "fukl": "full",
        }

        self.phrase_map = {
            r"\bhi hru\b": "Hi, how are you",
            r"\bhey hru\b": "Hey, how are you",
            r"\bhello hru\b": "Hello, how are you",
            r"\byo hru\b": "Yo, how are you",
            r"\bhi wyd\b": "Hi, what are you doing",
            r"\bhey wyd\b": "Hey, what are you doing",
            r"\byo wyd\b": "Yo, what are you doing",
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
            {"$setOnInsert": {"enabled": True, "target_commands": self.default_target_commands}},
            upsert=True,
        )

    async def on_plugins_ready(self):
        await self.patch_commands()

    async def cog_unload(self):
        await self.unpatch_commands()

    async def get_config(self):
        data = await self.coll.find_one({"_id": "config"})
        if not data:
            data = {"_id": "config", "enabled": True, "target_commands": self.default_target_commands}
            await self.coll.insert_one(data)
        return data

    async def update_config(self, **kwargs):
        await self.coll.update_one({"_id": "config"}, {"$set": kwargs}, upsert=True)

    def make_embed(self, title, description, color=discord.Color.blurple()):
        return discord.Embed(title=title, description=description, color=color)

    def fix_tokens(self, text):
        parts = re.split(r"(\s+)", text)
        return "".join(self.word_map.get(part.lower(), part) for part in parts)

    def fix_common_patterns(self, text):
        text = re.sub(r"\bim\b", "I'm", text, flags=re.IGNORECASE)
        text = re.sub(r"\bive\b", "I've", text, flags=re.IGNORECASE)
        text = re.sub(r"\bill\b", "I'll", text, flags=re.IGNORECASE)
        text = re.sub(r"\bid\b", "I'd", text, flags=re.IGNORECASE)
        text = re.sub(r"\bi\b", "I", text)
        text = re.sub(r"\s+([,.!?])", r"\1", text)
        text = re.sub(r"([,.!?])([A-Za-z])", r"\1 \2", text)
        text = re.sub(r"[ 	]{2,}", " ", text)
        return text.strip()

    def smart_capitalize(self, text):
        if not text:
            return text
        text = text[0].upper() + text[1:]

        def repl(match):
            return match.group(1) + match.group(2).upper()

        return re.sub(r"([.!?]\s+)([a-z])", repl, text)

    def add_punctuation(self, text):
        if not text:
            return text
        stripped = text.rstrip()
        if stripped.endswith(("!", "?", ".", "...")):
            return stripped

        lowered = stripped.lower()
        question_starts = (
            "how", "what", "why", "when", "where", "who", "are", "is",
            "do", "did", "does", "can", "could", "would", "will", "have",
            "has", "had", "should"
        )
        excited_starts = ("hi", "hello", "hey", "yo", "thanks", "thank you")

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
        corrected = re.sub(r"\byo,?\s+how are you\b", "Yo, how are you", corrected, flags=re.IGNORECASE)

        if corrected:
            corrected = corrected[0].upper() + corrected[1:]

        return corrected

    def _command_matches(self, command, names):
        if command is None:
            return False

        all_names = {command.name.lower(), command.qualified_name.lower()}
        all_names.update(alias.lower() for alias in command.aliases)

        for name in names:
            if name.lower() in all_names:
                return True
        return False

    def _get_signature(self, callback):
        try:
            return inspect.signature(callback)
        except Exception:
            return None

    def _find_string_targets(self, bound):
        targets = []

        for name, value in bound.arguments.items():
            lowered = name.lower()
            if lowered in {"self", "ctx", "context"}:
                continue
            if not isinstance(value, str):
                continue

            if lowered in self.preferred_param_names:
                targets.append(("named", name))
                continue

        if targets:
            return targets

        for name, value in reversed(list(bound.arguments.items())):
            lowered = name.lower()
            if lowered in {"self", "ctx", "context"}:
                continue
            if isinstance(value, str):
                targets.append(("named", name))
                break

        return targets

    async def patch_commands(self):
        config = await self.get_config()
        target_names = [x.lower() for x in config.get("target_commands", self.default_target_commands)]

        for command in self.bot.walk_commands():
            if not self._command_matches(command, target_names):
                continue

            key = command.qualified_name.lower()
            if key in self.patched_commands:
                continue

            original = command.callback
            signature = self._get_signature(original)
            if signature is None:
                continue

            @wraps(original)
            async def wrapped(*args, __original=original, __signature=signature, **kwargs):
                cfg = await self.get_config()
                if not cfg.get("enabled", True):
                    return await __original(*args, **kwargs)

                try:
                    bound = __signature.bind_partial(*args, **kwargs)
                except Exception:
                    return await __original(*args, **kwargs)

                changed = False
                targets = self._find_string_targets(bound)

                for kind, target in targets:
                    if kind == "named":
                        original_text = bound.arguments.get(target)
                        if isinstance(original_text, str):
                            corrected_text = self.autocorrect_text(original_text)
                            if corrected_text != original_text:
                                bound.arguments[target] = corrected_text
                                changed = True

                if changed:
                    return await __original(*bound.args, **bound.kwargs)

                return await __original(*args, **kwargs)

            self.patched_commands[key] = {"command": command, "original": original}
            command.callback = wrapped

    async def unpatch_commands(self):
        for data in self.patched_commands.values():
            data["command"].callback = data["original"]
        self.patched_commands.clear()

    @commands.group(name="autocorrect", invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_group(self, ctx):
        config = await self.get_config()
        targets = config.get("target_commands", self.default_target_commands)

        embed = discord.Embed(title="AutoCorrect Settings", color=discord.Color.blurple())
        embed.add_field(name="Enabled", value="Yes" if config.get("enabled", True) else "No", inline=False)
        embed.add_field(name="Patched Commands", value=", ".join(f"`{x}`" for x in targets) or "None", inline=False)
        embed.add_field(
            name="Commands",
            value=(
                f"`{ctx.prefix}autocorrect enable`\n"
                f"`{ctx.prefix}autocorrect disable`\n"
                f"`{ctx.prefix}autocorrect test <text>`\n"
                f"`{ctx.prefix}autocorrect listcmds`\n"
                f"`{ctx.prefix}autocorrect addcmd <command>`\n"
                f"`{ctx.prefix}autocorrect removecmd <command>`\n"
                f"`{ctx.prefix}autocorrect resetcmds`\n"
                f"`{ctx.prefix}autocorrect repatch`"
            ),
            inline=False,
        )
        await ctx.send(embed=embed)

    @autocorrect_group.command(name="enable")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_enable(self, ctx):
        await self.update_config(enabled=True)
        await ctx.send(embed=self.make_embed("AutoCorrect Enabled", "Reply, anonymous reply, and snippet-style commands will now autocorrect.", discord.Color.green()))

    @autocorrect_group.command(name="disable")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_disable(self, ctx):
        await self.update_config(enabled=False)
        await ctx.send(embed=self.make_embed("AutoCorrect Disabled", "Target commands will no longer autocorrect.", discord.Color.orange()))

    @autocorrect_group.command(name="test")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_test(self, ctx, *, text):
        corrected = self.autocorrect_text(text)
        embed = discord.Embed(title="AutoCorrect Test", color=discord.Color.blurple())
        embed.add_field(name="Original", value=text[:1024], inline=False)
        embed.add_field(name="Corrected", value=corrected[:1024], inline=False)
        await ctx.send(embed=embed)

    @autocorrect_group.command(name="listcmds")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_listcmds(self, ctx):
        config = await self.get_config()
        targets = config.get("target_commands", self.default_target_commands)
        await ctx.send(embed=self.make_embed("Target Commands", "\n".join(f"`{x}`" for x in targets) or "None set."))

    @autocorrect_group.command(name="addcmd")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_addcmd(self, ctx, command_name: str):
        config = await self.get_config()
        targets = list(config.get("target_commands", self.default_target_commands))

        if command_name.lower() in [x.lower() for x in targets]:
            return await ctx.send(embed=self.make_embed("Already Added", f"`{command_name}` is already in the target list.", discord.Color.orange()))

        targets.append(command_name)
        await self.update_config(target_commands=targets)
        await self.unpatch_commands()
        await self.patch_commands()
        await ctx.send(embed=self.make_embed("Command Added", f"`{command_name}` was added and the plugin repatched commands.", discord.Color.green()))

    @autocorrect_group.command(name="removecmd")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_removecmd(self, ctx, command_name: str):
        config = await self.get_config()
        targets = list(config.get("target_commands", self.default_target_commands))
        new_targets = [x for x in targets if x.lower() != command_name.lower()]

        if len(new_targets) == len(targets):
            return await ctx.send(embed=self.make_embed("Not Found", f"`{command_name}` is not in the target list.", discord.Color.orange()))

        await self.update_config(target_commands=new_targets)
        await self.unpatch_commands()
        await self.patch_commands()
        await ctx.send(embed=self.make_embed("Command Removed", f"`{command_name}` was removed and the plugin repatched commands.", discord.Color.green()))

    @autocorrect_group.command(name="resetcmds")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_resetcmds(self, ctx):
        await self.update_config(target_commands=self.default_target_commands)
        await self.unpatch_commands()
        await self.patch_commands()
        await ctx.send(embed=self.make_embed("Commands Reset", "Target commands were reset to the defaults, including `.s` and `.a`.", discord.Color.green()))

    @autocorrect_group.command(name="repatch")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autocorrect_repatch(self, ctx):
        await self.unpatch_commands()
        await self.patch_commands()
        await ctx.send(embed=self.make_embed("Repatch Complete", "The plugin repatched all target commands.", discord.Color.green()))


async def setup(bot):
    await bot.add_cog(AutoCorrect(bot))
