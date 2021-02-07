import discord
from methods.embed import create_embed, add_field
import shlex
from methods.database import database_connection

# !roles
# TODO: Fix error when a user uses !role with an invalid role.  Currently get an list index out of range error:
"""
Ignoring exception in on_message
Traceback (most recent call last):
  File "/home/pi/.local/lib/python3.7/site-packages/discord/client.py", line 333, in _run_event
    await coro(*args, **kwargs)
  File "main.py", line 53, in on_message
    await command_list[command](ctx, client)
  File "/home/pi/Desktop/BorgV2/commands/roles.py", line 22, in role
    .fetchall()[0][0]
IndexError: list index out of range
"""


async def role(ctx, client):
    users_roles = [i.id for i in ctx.author.roles]

    db = await database_connection(ctx.guild.id)
    content = shlex.split(ctx.content)

    if len(content) == 2:
        # Role
        role_name = content[1]
        role_id = 10
        role_id = (
            db["db"]
            .execute(
                "SELECT role_id FROM normal_roles WHERE command = (?)", (role_name,)
            )
            .fetchall()[0][0]
        )
        print(role_id)

        if role_id in users_roles:
            # Remove the role
            await ctx.author.remove_roles(ctx.guild.get_role(role_id))

            embed = create_embed(
                "Removed Role",
                f"{ctx.author.mention} removed role {ctx.guild.get_role(role_id).mention}.",
                "orange",
            )
            await ctx.channel.send(embed=embed)
        else:
            # Add the role
            await ctx.author.add_roles(ctx.guild.get_role(role_id))

            embed = create_embed(
                "Added Role",
                f"{ctx.author.mention} added role {ctx.guild.get_role(role_id).mention}.",
                "orange",
            )
            await ctx.channel.send(embed=embed)
    else:
        await roles(ctx, client)


async def roles(ctx, client):
    db = await database_connection(ctx.guild.id)

    full_roles = [i for i in db["db"].execute("SELECT * FROM normal_roles")]

    embed = create_embed("Roles", "", "orange")
    for role in full_roles:
        add_field(
            embed, f"!role {role[1]}", f"{ctx.guild.get_role(role[0]).mention}", True
        )

    await ctx.channel.send(embed=embed)


async def create_role(ctx, client):
    content = shlex.split(ctx.content)

    if ctx.author.guild_permissions.administrator != True:
        # Does not have permission
        return

    if len(content) != 3:
        # Provided no commandline arguments, print out a help message
        embed = create_embed("Create_role", "!create_role {role} {name}", "orange")
        add_field(
            embed,
            "role",
            "Provide the @ for the role (ie. @Member) or the name of the role (ie. Member)",
            True,
        )
        add_field(
            embed,
            "name",
            "Provide the name for the user to add the role (ie. member or 'cool guy')",
            True,
        )
        await ctx.channel.send(embed=embed)
        return

    # Role as an @ <@&749382234829750392>
    # Otherwise: Member

    role = content[1]
    name = content[2]

    db = await database_connection(ctx.guild.id)

    if role[0:2] == "<@":
        # Actual Role @ provided
        role_id = role[3:-1]
    else:
        role_id = [i.id for i in ctx.guild.roles if i.name == role]

        if len(role_id) == 1:
            role_id = role_id[0]
        else:
            #! Error Message
            embed = create_embed(
                "Error",
                "The 'role' provided is invalid.  Make sure it's spelled correctly with proper capitalization (case sensitive) and consider trying to use the actual @ for the role.",
                "red",
            )
            await ctx.channel.send(embed=embed)

            return

    if int(role_id) not in [
        i[0] for i in db["db"].execute("SELECT role_id FROM normal_roles").fetchall()
    ] and name not in [
        i[0] for i in db["db"].execute("SELECT command FROM normal_roles").fetchall()
    ]:
        for role in ctx.guild.roles:
            if role.name == "Borg Test" or role.name == "Borg":
                BORG_ROLE = {"id": role.id, "position": role.position}

        if BORG_ROLE["position"] > ctx.guild.get_role(int(role_id)).position:
            db["db"].execute("INSERT INTO normal_roles VALUES (?, ?)", (role_id, name))
            db["con"].commit()

            embed = create_embed("Role Added", "", "light_green")
            add_field(embed, "Role", ctx.guild.get_role(int(role_id)).mention, True)
            add_field(embed, "Command", f"!role {name}", True)

            await ctx.channel.send(embed=embed)
        else:
            embed = create_embed(
                "Error",
                "The bot does not have permission to give that role to users.  Ensure that the 'Borg' role is ABOVE the role in the 'Roles' part of your settings.",
                "red",
            )
            await ctx.channel.send(embed=embed)

    else:
        # Error Message
        embed = create_embed(
            "Error",
            "The 'role' or 'name' already has a command associated.  Check the list of roles with !roles.",
            "red",
        )

        await ctx.channel.send(embed=embed)


async def remove_role(ctx, client):
    db = await database_connection(ctx.guild.id)

    content = shlex.split(ctx.content)

    if len(content) != 2:
        embed = create_embed("Remove_role", "!remove_role {role}", "orange")
        add_field(
            embed,
            "role",
            "The actual role to remove from !roles (ie. Member or @Member)",
            True,
        )
        await ctx.channel.send(embed=embed)
        return

    role = content[1]
    if role[0:2] == "<@":
        # Actual Role @ provided
        role_id = role[3:-1]
    else:
        role_id = [i.id for i in ctx.guild.roles if i.name == role]

        if len(role_id) == 1:
            role_id = role_id[0]
        else:
            #! Error Message
            embed = create_embed(
                "Error",
                "The 'role' provided is invalid.  Make sure it's spelled correctly with proper capitalization (case sensitive) and consider trying to use the actual @ for the role.",
                "red",
            )
            await ctx.channel.send(embed=embed)

            return

    removal_role = (
        db["db"]
        .execute("SELECT * FROM normal_roles WHERE role_id = (?)", (int(role_id),))
        .fetchall()[0]
    )

    db["db"].execute(
        "DELETE FROM normal_roles WHERE role_id = (?)", (int(removal_role[0]),)
    )
    db["con"].commit()

    embed = create_embed("Role Removed", "", "dark_blue")
    add_field(
        embed, "Role", f"{ctx.guild.get_role(int(removal_role[0])).mention}", True
    )
    add_field(embed, "Command", f"!role {removal_role[1]}", True)

    await ctx.channel.send(embed=embed)
