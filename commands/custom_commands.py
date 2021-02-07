import discord
import shlex
from methods.embed import create_embed, add_field
from methods.database import database_connection, settings_location
import yaml

# TODO: Add back happyboi command


async def create_command(ctx, client):
    # Todo: !create_command !commandname 'text here'

    if ctx.author.guild_permissions.administrator != True:
        return

    db = await database_connection(ctx.guild.id)

    content = shlex.split(ctx.content, posix=False)

    if len(content) != 3:
        embed = create_embed(
            "Create_command",
            "!create_command {'!command name'} {'description'}",
            "orange",
        )
        add_field(
            embed,
            "command name",
            "The 'name' of the command (ie. !info or !welcome).",
            True,
        )
        add_field(
            embed,
            "description",
            'The actual text provided by the command (ie. "Information can be found here: https://wikipedia.com"',
            True,
        )
        example_list = """```
- item 1
- item 2
- item 3
- etc...```"""
        add_field(
            embed,
            "Hint",
            f'If you want to add multiple lines OR use a space (for example, as Code or as a list.  You\'ll need to use qutoation marks ("").  Example: !create_command !list "Here is a list: "{example_list}"',
            True,
        )

        await ctx.channel.send(embed=embed)
        return

    command = content[1]
    description = content[2]

    with open(await settings_location(ctx.guild.id)) as f:
        l = yaml.safe_load(f)
        command_list = []
        for group in l["default_commands"]:
            for c in l["default_commands"][group]:
                if type(c) == str:
                    command_list.append(c)

    command_list += [
        i[0][1::]
        for i in db["db"].execute("SELECT command FROM custom_commands").fetchall()
    ]

    if command[1::] in command_list:
        embed = create_embed(
            "Error",
            "That command is already a registerd command for this server.",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    if description[0] == '"' and description[-1] == '"':
        description = description[1:-1]

    db["db"].execute(
        "INSERT INTO custom_commands VALUES (?, ?)",
        (
            command,
            description,
        ),
    )
    db["con"].commit()

    embed = create_embed("Command Created Successfully.", "", "light_green")
    add_field(embed, "Command", command, True)
    add_field(embed, "Description", description, True)

    await ctx.channel.send(embed=embed)


async def remove_command(ctx, client):
    if ctx.author.guild_permissions.administrator != True:
        return

    content = shlex.split(ctx.content)

    db = await database_connection(ctx.guild.id)

    if len(content) != 2:
        embed = create_embed("Remove_command", "!remove_command {command}", "orange")
        add_field(
            embed,
            "command",
            "The command you would like to remove (ie. !info or !hello)",
            True,
        )

        await ctx.channel.send(embed=embed)
        return

    command = content[1]

    command_list = [
        i for i in db["db"].execute("SELECT * FROM custom_commands").fetchall()
    ]

    for c in command_list:
        if c[0] == command:
            db["db"].execute(
                "DELETE FROM custom_commands WHERE command = (?)", (command,)
            )
            db["con"].commit()

            embed = create_embed("Command Removed Successfully.", "", "dark_blue")
            add_field(embed, "command", c[0], True)
            add_field(embed, "description", c[1], True)

            await ctx.channel.send(embed=embed)

        else:
            embed = create_embed(
                "Error",
                "Invalid Command to Remove.  Try checking all of the commands with !commands",
                "red",
            )

            await ctx.channel.send(embed=embed)
            return


async def check_custom_command(ctx, client, command):
    db = await database_connection(ctx.guild.id)

    command_list = [
        i for i in db["db"].execute("SELECT * FROM custom_commands").fetchall()
    ]

    for c in command_list:
        if f"!{command}" == c[0]:
            embed = create_embed(f"{command.capitalize()}", f"{c[1]}", "orange")
            await ctx.channel.send(embed=embed)


async def commands(ctx, client):
    # TODO
    db = await database_connection(ctx.guild.id)

    command_list = [
        i[0] for i in db["db"].execute("SELECT command FROM custom_commands").fetchall()
    ]
    if len(command_list) >= 1:
        final = """```"""

        for command in command_list:
            final += command + "\n"

        final += "```"

        embed = create_embed("Commands", final, "orange")
        await ctx.channel.send(embed=embed)
    else:
        embed = create_embed(
            "Error",
            "There are currently no commands!  Ask an admin to use !create_command",
            "red",
        )
        await ctx.channel.send(embed=embed)