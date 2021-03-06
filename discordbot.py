# Copyright © 2021 Compsup

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import discord
from discord.ext import commands
import asyncio
import json
import logging
from better_profanity import profanity
import os
import random
import string
version = "1.2.11"
global modules
global settings

# Default config options

settings = {
    "version": "1.2.11",
    "logging-level": "warn",
    "raidmode": False,
    "shutdowncode": f"{''.join(random.choice(string.ascii_lowercase) for i in range(32))}",
}
modules = {
    "swear": True,
    "goodboy": True,
}

devmode = False
userstrikes = {}
# Logging
logging.basicConfig(filename="logfile.log", format='%(asctime)s %(message)s', filemode='a')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
# Retrive all the badwords
profanity.load_censor_words_from_file("swearwords.txt")

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='?', intents=intents)


async def updater():
    # Check for update
    if settings["version"] != version:
        logger.info(f'Bot Updated from {settings["version"]} to {version}')
        print(f'Bot Updated from {settings["version"]} to {version}')
        settings["version"] = version

        ###################
        # Custom code to run per update
        ###################
        await settings_manager("save")

@bot.event
async def on_ready():
    await module_manager("load")
    await settings_manager("load")
    await updater()

    if settings["logging-level"] == "debug":
        logger.setLevel(logging.DEBUG)
    elif settings["logging-level"] == "warn":
        logger.setLevel(logging.WARN)
    elif settings["logging-level"] == "critical":
        logger.setLevel(logging.CRITICAL)
    elif settings["logging-level"] == "error":
        logger.setLevel(logging.ERROR)
    elif settings["logging-level"] == "info":
        logger.setLevel(logging.INFO)

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print("Connected to: " + str(len(bot.guilds)) + " servers!")
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f'Version: {str(settings["version"])}'))
    logger.info("Ready!")

async def settings_manager(arg):
    global settings
    if arg == "save":
        logger.debug("Saving Settings")
        with open("settings.json", "w") as file:
            file.write(json.dumps(settings, indent=4))
    elif arg == "load":
        # Try reading, if it fails try creating the file.
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                logger.debug("Loaded Settings")
        except:
            logger.warning("Reading failed, trying to create settings.json.")
            with open("settings.json", "w") as file:
                data = json.dumps(settings, indent=4)
                file.write(data)
                logger.debug("Created settings.json and saved.")
    else:
        # Why, just why. Please do this right. Whats hard about passing a proper arg?
        logger.error("Improper arg passed in settings manager")
        pass
async def user_strike_manager(message, userstrikes):
    time = 600
    user = message.author.id
    if user not in userstrikes:
        userstrikes[user] = 1
    else:
        userstrikes[user] += 1
        if userstrikes[user] >= 3:
            logger.debug("User: " + str(message.author) + " has been muted due to maxing strikes")
            print("User: " + str(message.author) + " has maxed there strikes!")
            member = message.author
            role = discord.utils.get(member.guild.roles, name="BAD BAD")
            await member.add_roles(role)
            embed = discord.Embed(title=f"{member}", description=f"has been muted from text and voice for {time} seconds", color=0xFF5733)
            await message.channel.send(embed=embed)
            await asyncio.sleep(time)
            await member.remove_roles(role)
            embed = discord.Embed(title=f"Unmuted", description=f"You have been unmuted in {message.guild}", color=0x258E70)
            await member.send(embed=embed)
            userstrikes[user] = 0
            logger.debug("User: " + str(message.author) + " has been unmuted.")
async def module_manager(arg):
    global modules
    if arg == "save":
        logger.debug("Saving Settings")
        with open("modules.json", "w") as file:
            data = json.dumps(modules, indent=4)
            file.write(data)
    if arg == "load":
        # Try reading, if it fails try creating the file.
        try:
            with open("modules.json", "r") as file:
                data = file.read()
                modules = json.loads(data)
                logger.debug("Loaded Settings")
        except:
            logger.warning("Reading failed, trying to create modules.json.")
            with open("modules.json", "w") as file:
                data = json.dumps(modules, indent=4)
                file.write(data)
                logger.debug("Created modules.json and saved.")
async def incident_report(ctx, message : str):
    logger.warninging(f"Incident Report: {message}")
    admins = {
        "compsup": 703423921860509698,
        "XTheMoose": 621069526615720008,
        "TomBomb": 549048335961686026,
    }
    embed = discord.Embed(title=f'Incident Report', description=message, color=0xFF0000)
    for x in admins:
        user = bot.get_user(int(admins[x]))
        await user.send(embed=embed)

async def counting(message):
     if str(message.channel.id) == "766025171038896128":
        # Check if the string is numeric
        if message.content.isnumeric():
            counting = {
                "last_user": "",
                "current_num": 0,
            }
            with open("counting.json", "r") as f:
                try:
                    counting = json.load(f)
                except:
                    with open("counting.json", "w") as f:
                        json.dump(counting, f)
            counting["current_num"] += 1
            if str(message.content) == str(counting["current_num"]) and str(message.author) != counting["last_user"]:
                await message.add_reaction("✅")
                counting["last_user"] = str(message.author)
                with open("counting.json", "w") as f:
                    json.dump(counting, f)
            elif str(message.author) == counting["last_user"]:
                await message.add_reaction("❌")
                await message.channel.send(f'{message.author.mention} counted twice!')
                with open("counting.json", "w") as f:
                    counting["current_num"] = 0
                    counting["last_user"] = ""
                    json.dump(counting, f)
                    logger.debug("Counting reset to 0")
            else:
                await message.add_reaction("❌")
                await message.channel.send(f'{message.author.mention} put in a wrong number! The next number was {counting["current_num"]}')
                with open("counting.json", "w") as f:
                    counting["current_num"] = 0
                    counting["last_user"] = ""
                    json.dump(counting, f)
                    logger.debug("Counting reset to 0")
@bot.event
async def on_message(message):
    message_content = message.content.lower()
    message_content = message_content.replace("*", "")
    # Ignore empty messages like photos
    if message_content == "":
        return
    # Don't trigger on the bots messages
    if message.author == bot.user:
        return

    if modules["swear"]:
        logger.debug("Swear triggered")
        Admin = discord.utils.get(message.guild.roles, name="Admin")
        bot_builder = discord.utils.get(message.guild.roles, name="Bot Builder")
        # Exempt Admin and bot builder
        if not Admin in message.author.roles or devmode:
            if not bot_builder in message.author.roles or devmode:
                # Uses Better Profanity to check if the string contains 1 or more bad words.
                if profanity.contains_profanity(message_content):
                    logger.debug(f'{message.author} said a bad word: {message_content}')
                    print("here")
                    await message.delete()
                    #await user_strike_manager(message, userstrikes)
    await counting(message)
    await bot.process_commands(message)

@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        guild = bot.get_guild(744594255456239636)
        member = guild.get_member(after.id)
        if profanity.contains_profanity(after.nick):
            await member.edit(nick=None)
            await member.send("You username contains profanity and has been changed!")
            logger.debug(f"{member.name} made there nickname a bad word and has been changed.")
async def roles(ctx):
    embed=discord.Embed(title="Reaction Roles", description="React with the corresponding emoji to get the role", color=0xff0000)
    embed.add_field(name="🎉", value="LETS PARTY", inline=True)
    embed.add_field(name="⛏️", value="MC Party", inline=True)
    embed.add_field(name="<:AmongUsRed:842015690348036128>", value="Among Us Party", inline=True)
    embed.add_field(name="👻", value="Phasmophobia Party", inline=True)
    embed.set_footer(text="Made by @compsup")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('🎉')
    await msg.add_reaction('⛏️')
    await msg.add_reaction('<:AmongUsRed:842015690348036128>')
    await msg.add_reaction('👻')
@bot.event
async def on_raw_reaction_add(payload):
    if not payload.guild_id:
        return
    ourMessageID = 851821305605914704

    if ourMessageID == payload.message_id:
        member = payload.member
        guild = member.guild
        emoji = payload.emoji.name
        if emoji == '🎉':
            mrole = discord.utils.get(guild.roles, name='LETS PARTY')
            await member.add_roles(mrole)
        elif emoji == '⛏️':
            mrole = discord.utils.get(guild.roles, name='MC Party')
            await member.add_roles(mrole)
        elif emoji == 'AmongUsRed':
            mrole = discord.utils.get(guild.roles, name='Among Us Party')
            await member.add_roles(mrole)
        elif emoji == '👻':
            mrole = discord.utils.get(guild.roles, name='Phasmophobia Party')
            await member.add_roles(mrole)
@bot.event
async def on_raw_reaction_remove(payload):
    if not payload.guild_id:
        return
    ourMessageID = 851821305605914704
    if ourMessageID == payload.message_id:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = payload.emoji.name
        if emoji == '🎉':
            mrole = discord.utils.get(guild.roles, name='LETS PARTY')
            await member.remove_roles(mrole)
        elif emoji == '⛏️':
            mrole = discord.utils.get(guild.roles, name='MC Party')
            await member.remove_roles(mrole)
        elif emoji == 'AmongUsRed':
            mrole = discord.utils.get(guild.roles, name='Among Us Party')
            await member.remove_roles(mrole)
        elif emoji == '👻':
            mrole = discord.utils.get(guild.roles, name='Phasmophobia Party')
            await member.remove_roles(mrole)

@bot.event
async def on_member_join(member):
    if settings["raidmode"]:
        await member.kick(reason="Server in lockdown mode!")
@bot.command()
async def ping(ctx):
    await ctx.send("pong!")
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def editnick(self, ctx, user : discord.Member, newnick):
        await user.edit(nick=str(newnick))
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def purge(self, ctx, arg):
        await ctx.channel.purge(limit=int(arg), bulk=True)

    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def tempmute(self, ctx, member : discord.Member, time):
        '''
        Tempmutes a user for the amount of time
        '''
        muterole = discord.utils.get(member.guild.roles, name="BAD BAD")
        await member.add_roles(muterole)
        embed = discord.Embed(title=f"{member}", description=f"has been muted from text and voice for {int(time)} seconds", color=0xFF5733)
        msg = await ctx.channel.send(embed=embed)
        await asyncio.sleep(int(time))
        await member.remove_roles(muterole)
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def mute(self, ctx, member : discord.Member, time):
        '''
        mutes a user
        '''
        muterole = discord.utils.get(member.guild.roles, name="BAD BAD")
        await member.add_roles(muterole)
        embed = discord.Embed(title=f"{member}", description=f"has been muted from text and voice for infinite seconds", color=0xFF5733)
        msg = await ctx.channel.send(embed=embed)
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def unmute(self, ctx, member : discord.Member):
        '''
        Unmutes a user
        '''
        muterole = discord.utils.get(member.guild.roles, name="BAD BAD")
        await member.remove_roles(muterole)
        embed = discord.Embed(title=f"Unmuted", description=f"You have been unmuted in {ctx.guild}", color=0x258E70)
        await member.send(embed=embed)
        embed = discord.Embed(title=f"{member}", description=f"has been unmuted.", color=0x258E70)
        await ctx.channel.send(embed=embed)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def pog(self, ctx):
        await ctx.send("Bark- You are as stupid as a dog.")

    @commands.command()
    async def goodboy(self, ctx):
        if modules["goodboy"]:
            embed = discord.Embed(title="Woof", description="Thank you!", color=0xFF5733)
            await ctx.send(embed=embed)
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def poll(self, ctx, seconds: int, *, question: str):
        poll_upthumb = 0
        poll_downthumb = 0
        await ctx.message.delete()
        embed = discord.Embed(title=f'Poll - {ctx.author}', description=f"{question}\n\n Yes/No({str(seconds)}seconds)", color=0xC9DEF2)
        msg = await ctx.send(embed=embed)
        messageid = msg.id
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')
        await asyncio.sleep(seconds)
        message = await ctx.fetch_message(messageid)
        for emoji in message.reactions:
            if str(emoji) == "👍":
                poll_upthumb = emoji.count
            elif str(emoji) == "👎":
                poll_downthumb = emoji.count

        # To correct for the bot reacting
        poll_upthumb -= 1
        poll_downthumb -= 1
        embed = discord.Embed(title=f'Poll Results', description=f"{question}\n\nYes: {poll_upthumb}\n No: {poll_downthumb}", color=0x002abf)
        await ctx.send(embed=embed)
class Administrator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def start(self, ctx, arg):
        arg = str(arg).lower()
        global modules
        if arg in modules:
            modules[arg] = True
            await ctx.channel.send(f"{arg} has been started.")
            await module_manager("save")
    @commands.command()
    async def changelog(self, ctx):
        try:
            with open('changelog.txt', 'r') as f:
                content = f.read()
                if content == "":
                    await ctx.channel.send("No changelog available")
                else:
                    await ctx.channel.send(content)
        except Exception as e:
            print(e)
            with open('changelog.txt', 'w') as f:
                logger.info("Created changelog.txt")
            with open('changelog.txt', 'r') as f:
                content = f.read()
                if content == "":
                    await ctx.channel.send("No changelog available")
                else:
                    await ctx.channel.send(content)
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def raidmode(self, ctx, arg):
        if arg == "enable":
            settings["raidmode"] = True
            await settings_manager("save")
            await ctx.channel.send("Raid mode enabled")
        elif arg == "disable":
            settings["raidmode"] = False
            await settings_manager("save")
            await ctx.channel.send("Raid mode disabled")
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def stealthmode(self, ctx, arg : str):
        '''
        Makes the bot turn invisible
        Usage: ?stealthmode <enable/disable>
        '''
        if arg == "enable":
            await bot.change_presence(status=discord.Status.offline)
        if arg == "disable":
            await bot.change_presence(status=discord.Status.online)
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def shutdown(self, ctx, arg):
        arg = str(arg)
        content = str(settings['shutdowncode'])
        if arg in content:
            print("Shutting down...")
            logger.warninging(f"! {ctx.message.author} Shutdown the bot !")
            await ctx.channel.send(f"! Emergency Shutdown Initated !")
            await ctx.channel.send(f"Shutting Down Modules:")
            await ctx.channel.send(f"System Shutting down...")
            raise SystemExit
        else:
            embed = discord.Embed(title=f'Incident Warning', description=f"Incorrect Password. This incident will be reported.", color=0xFF0000)
            await ctx.channel.send(embed=embed)
            logger.warninging(f"User tried to shutdown the bot with incorrect password[{content}]")
            await incident_report(ctx, f"Attempted bot shutdown by {ctx.message.author}, invalid password.")

        
    @commands.command()
    async def strikes(self, ctx):
        user = ctx.author.id
        if user in userstrikes:
            await ctx.channel.send("You have " + str(userstrikes[user]) + " strikes.")
        else:
            await ctx.channel.send("You don't have any strikes!")
    @commands.command()
    @commands.has_role('Bot Builder')
    async def setstrikes(self, ctx, user : discord.Member, num):
        global userstrikes
        user = user.id
        if user in userstrikes:
            userstrikes[user] = float(num)
        else:
            userstrikes[user] = float(num)

        
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def createreactionroles(self, ctx):
        await roles(ctx)
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def devmode(self, ctx):
        '''
        Enables devmod

        Devmode makes it so all features work on everyone.
        '''
        global devmode
        if devmode:
            logger.debug(f'Dev mode has been disabled by: {ctx.author}')
            print(f'Dev mode has been disabled by: {ctx.author}')
            devmode = False
            await ctx.channel.send("Dev mode: Disabled")
        else:
            logger.debug(f'Dev mode has been enabled by: {ctx.author}')
            print(f'Dev mode has been enabled by: {ctx.author}')
            devmode = True
            await ctx.channel.send("Dev mode: Enabled")
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def addbadword(self, ctx, arg):
        arg = str(arg).lower()
        with open("swearwords.txt", "a") as file:
            file.write("\n" + arg)
        profanity.load_censor_words_from_file("swearwords.txt")
        await ctx.message.delete()
    @commands.command()
    @commands.has_any_role('Admin', 'Bot Builder')
    async def stop(self, ctx, arg):
        arg = str(arg).lower()
        global modules
        if arg in modules:
            modules[arg] = False
            await ctx.channel.send(f"{arg} has been stopped.")
            await module_manager("save")

@bot.event
async def on_command_error(ctx, error):
    '''
    Handle common errors
    '''
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("No private messages.")
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send("You don't have the permissions to do that!")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("You don't have the permissions to do that!")
    else:
        logger.error(error)
bot.add_cog(Moderation(bot))
bot.add_cog(Fun(bot))
bot.add_cog(Administrator(bot))

try:
    with open("token.txt", "r") as file:
        token = file.read()
except FileNotFoundError:
    print("Critical Error: No token file found! Please put a token into 'token.txt': https://discord.com/developers/applications")
    raise SystemExit
bot.run(token)