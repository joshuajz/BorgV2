import discord
import os
import traceback
from commands import *
from methods.database import create_filesystem, settings_location, database_connection
import yaml

# Intents
intents = discord.Intents().default()
intents.members = True
intents.reactions = True

# TODO: Potentially change programs commands, and cange the commands in general so they're more consistant

# TODO: Setup a bot channel where all messages are deleted after being sent (after a timeout)

# Commmands
command_list = {
    "help": help_command,
    "create_role": create_role,
    "roles": roles,
    "role": role,
    "remove_role": remove_role,
    "create_command": create_command,
    "remove_command": remove_command,
    "commands": commands,
    "programs_setup": programs_setup,
    "programs_add": programs_add,
    "programs": programs,
    "programs_remove": programs_remove,
    # TEMPPPPP
    "welcome_setup": welcome_setup,
    "welcome_toggle": welcome_toggle,
    "warn": warn,
    "userinfo": userinfo,
}

# Bot Instance
client = discord.Client(intents=intents)

# All of the "Extensions" or "Cogs" the bot starts with
startup_extensions = []


@client.event
async def on_ready():
    print(f"Logged in as {client.user}.")
    await create_filesystem(client)


@client.event
async def on_message(ctx):
    print(ctx.content)

    # Don't do anything with a bot's message
    if ctx.author == client.user:
        return

    if ctx.content.startswith("!"):
        command = ctx.content[1::].split(" ")[0].lower()
        if command in command_list:
            await command_list[command](ctx, client)
        else:
            await check_custom_command(ctx, client, command)


@client.event
async def on_raw_reaction_add(ctx):

    if ctx.member.bot:
        return

    if await program_reaction_handling(ctx, client) == True:
        return


@client.event
async def on_member_join(ctx):
    #! EDIT
    #! This is very temp
    await welcome_handling(ctx, client)
    # welcome_channel = 742523058975145985
    # await client.get_channel(welcome_channel).send(
    #     f"Welcome {ctx.mention} to {ctx.guild.name}!  Check out: https://www.notion.so/Waterloo-Admissions-Information-f8e72927a8804021aeafff7baefddcc9 for more information about admissions!"
    # )


# Runs the bot with the token in bot_token.txt
with open("bot_token.txt", "r") as f:
    client.run(f.readlines()[0])