import discord
from methods.database import database_connection
import shlex
from methods.embed import create_embed, add_field
import yaml
import re

# TODO: Editing

# TODO: Change Programs Add to a CSV


# ! REWRITING programs_add w/ a csv
async def programs_add(ctx, client):
    content_temp = ctx.content.split(" ")
    if len(ctx.content.split(" ")) <= 1 and len(ctx.content.split("\n")) <= 1:
        embed = create_embed(
            "Programs_add",
            "!programs_add {user (optional, admin only)} Program #1, Program #2, Program #3...",
            "orange",
        )

        add_field(
            embed,
            "user",
            "Admin Only: You can supply a user and their programs for them.",
            True,
        )

        add_field(
            embed,
            "Programs",
            "You'll provide a list of programs.  Seperate each program with a comma.",
            True,
        )

        add_field(embed, "Example", "!programs_add UW - CS, UW - SE", True)

        await ctx.channel.send(embed=embed)
        return

    db = await database_connection(ctx.guild.id)

    programs_channel = (
        db["db"].execute("SELECT programs_channel FROM settings").fetchone()[0]
    )

    if programs_channel is None:
        embed = create_embed(
            "Error",
            "The admins have not setup !programs.  Ask them to run !programs_setup.",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    programs_channel = int(programs_channel)

    content = "".join(list(ctx.content)[14::])

    add_programs = []

    if content[0:3] == "<@!":
        if ctx.author.guild_permissions.administrator == True:
            user_id = int(content[3:21])
        else:
            user_id = ctx.author.id

        content = content[23::]
    else:
        user_id = ctx.author.id

    user_id = int(user_id)

    if "\n" in content:
        for program in content.split("\n"):
            add_programs.append(program.strip())
        temp_list = []
        if "," in "".join(add_programs):
            for program in add_programs:
                if "," in program:
                    for p in program.split(","):
                        temp_list.append(p)
                else:
                    temp_list.append(program)

        add_programs = temp_list
    else:
        for program in content.split(","):
            add_programs.append(program.strip())

    current_programs = (
        db["db"]
        .execute("SELECT description FROM programs WHERE user_id = (?)", (user_id,))
        .fetchone()
    )

    embed = create_embed("Programs Verification Required", "", "magenta")
    add_field(embed, "User", client.get_user(user_id).mention, False)
    clist = ""
    if current_programs is not None:
        for p in current_programs[0].split("\n"):
            if p != "":
                clist += p + "\n"

        add_field(embed, "Current Programs", clist, True)
    plist = ""
    for p in add_programs:
        plist += p + "\n"

    add_field(embed, "Program Additions", plist, True)
    add_field(embed, "Final Programs", clist + plist, True)

    verification_msg = await client.get_channel(programs_channel).send(embed=embed)

    emojis = ["✅", "❌"]
    for emoji in emojis:
        await verification_msg.add_reaction(emoji)

    embed = create_embed(
        "Successfully Sent to Moderators",
        "Your !programs additions have been sent to the administrators for review.  Please sit tight!",
        "light_green",
    )
    add_field(embed, "User", client.get_user(int(user_id)).mention, True)
    add_field(embed, "Added Programs", plist, True)
    await ctx.channel.send(embed=embed)


async def programs_remove(ctx, client):
    content = shlex.split(ctx.content)

    db = await database_connection(ctx.guild.id)
    if len(content) <= 1:
        embed = create_embed("Programs_remove", "!programs_remove", "red")
        await ctx.channel.send(embed=embed)

    content = ctx.content.split("!programs_remove")[1]

    if content.strip()[0:3] == "<@!":
        if ctx.author.guild_permissions.administrator:
            user_id = int(content.strip()[3:21])
        else:
            user_id = ctx.author.id
        content = content.strip()[22::]
    else:
        user_id = ctx.author.id

    remove_list = []
    if "\n" in content:
        for i in content.split("\n"):
            if "," in i:
                for z in i.split(","):
                    remove_list.append(int(z.strip()))
            else:
                remove_list.append(int(i.strip()))
    elif "," in content:
        for i in content.split(","):
            remove_list.append(int(i.strip()))

    # Remove duplicates
    remove_list = list(dict.fromkeys(remove_list))

    programs_raw = (
        db["db"]
        .execute("SELECT description FROM programs WHERE user_id = (?)", (user_id,))
        .fetchone()[0]
        .split("\n")
    )

    programs = {}
    i = 1
    for p in programs_raw:
        programs[i] = p
        i += 1

    """if len(content) == 1:
        user_id = ctx.author.id
    elif len(content) == 2:
        if ctx.author.guild_permissions.administrator != True:
            embed = create_embed(
                "Error",
                "You do not have administrator permissions!  You cannot remove someone else's command!",
                "red",
            )
            await ctx.channel.send(embed=embed)
            return

        user_id = content[1][3:-1]
    else:
        embed = create_embed(
            "Programs_remove", "!programs_remove {admin only: user}", "orange"
        )
        add_field(
            embed, "user", "Admin Only: A user's command you'd like to remove.", True
        )
        await ctx.channel.send(embed=embed)
        return

    data = (
        db["db"]
        .execute("SELECT user_id from programs WHERE user_id = (?)", (int(user_id),))
        .fetchone()
    )

    if data is None:
        embed = create_embed(
            "Error",
            "That user does not have a !programs.  Ask them to create one!",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    db["db"].execute("DELETE FROM programs WHERE user_id = (?)", (int(user_id),))
    db["con"].commit()

    embed = create_embed("Programs Removed Successfully", "", "dark_blue")
    await ctx.channel.send(embed=embed)
    return"""


async def programs(ctx, client):
    content = shlex.split(ctx.content)

    db = await database_connection(ctx.guild.id)

    if len(content) != 2:
        embed = create_embed("Programs", "!programs {user}", "orange")
        add_field(
            embed, "user", "The user's programs you'd like to see. (ie. @JZ)", True
        )
        await ctx.channel.send(embed=embed)
        return

    # user_id = content[1][3:-1]
    user_id = int("".join([i for i in content[1] if i.isnumeric()]))

    db["db"].execute("SELECT * FROM programs WHERE user_id = (?)", (user_id,))

    user_data = db["db"].fetchone()

    if user_data is None:
        embed = create_embed(
            "Error",
            "That user hasn't created a !programs.  Create one with !programs_add",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    programs = user_data[1].split("\n")

    message = "```\n"
    for program in range(len(programs)):
        if programs[program] != "":
            message += f"{program + 1}. {programs[program]}\n"
    message += "```"

    embed = create_embed(f"Programs", "", "orange")
    add_field(embed, "User", f"{client.get_user(int(user_id)).mention}", False)
    add_field(embed, "Programs", message, True)

    await ctx.channel.send(embed=embed)


async def programs_setup(ctx, client):
    if ctx.author.guild_permissions.administrator != True:
        return
    content = shlex.split(ctx.content)
    db = await database_connection(ctx.guild.id)

    if len(content) != 2:
        embed = create_embed("Programs_setup", "!programs_setup {channel}", "orange")
        add_field(
            embed,
            "channel",
            "The channel (ie. #mod-queue) or the name of the channel (ie. mod-queue).  When a user uses !programs_add, a moderator will have to 'accept' the submission for it to be useable with !programs.",
            True,
        )

        await ctx.channel.send(embed=embed)
        return

    channel = content[1]

    if channel[0:2] == "<#":
        # Real channel
        channel_id = channel[2:-1]
    else:
        # Name of a channel
        channel_id = [i.id for i in ctx.guild.channels if i.name == channel]

        if len(channel_id) == 1:
            channel_id = channel_id[0]
        else:
            #! Error Message
            embed = create_embed(
                "Error",
                "The channel provided is invalid.  Make sure it's spelled correctly with proper capitlization (case sensitive).  Consider trying to use the actual # for the channel (ie. #channel)",
                "red",
            )
            await ctx.channel.send(embed=embed)
            return

    db["db"].execute("UPDATE settings SET programs_channel = (?)", (channel_id,))
    db["con"].commit()

    embed = create_embed("Programs Setup Successfully", "", "light_green")
    add_field(
        embed, "channel", f"{ctx.guild.get_channel(int(channel_id)).mention}", True
    )
    await ctx.channel.send(embed=embed)


async def program_reaction_handling(ctx, client):
    db = await database_connection(ctx.guild_id)

    mod_channel_id = (
        db["db"].execute("SELECT programs_channel FROM settings").fetchone()[0]
    )
    if mod_channel_id is None:
        return False

    mod_channel_id = int(mod_channel_id)

    m = await client.get_channel(ctx.channel_id).fetch_message(ctx.message_id)
    m_embeds = m.embeds[0]

    if m.embeds[0].title != "Programs Verification Required":
        return

    if mod_channel_id != int(ctx.channel_id):
        return

    if ctx.emoji.name == "❌":
        await m.delete()
        return True
    elif ctx.emoji.name == "✅":
        programs = None
        user_id = None
        for embed in m_embeds.fields:
            print(embed.name)
            if embed.name == "Final Programs":
                programs = embed.value
            elif embed.name == "User":
                user_id = int(embed.value[2:-1])

        if programs and user_id:
            if (
                db["db"]
                .execute(
                    "SELECT COUNT(user_id) FROM programs WHERE user_id = (?)",
                    (user_id,),
                )
                .fetchone()[0]
                > 0
            ):
                db["db"].execute(
                    "UPDATE programs SET description = ? WHERE user_id = ?",
                    (programs, int(user_id)),
                )
            else:
                db["db"].execute(
                    "INSERT INTO programs (user_id, description) VALUES (?, ?) ",
                    (int(user_id), programs),
                )
            db["con"].commit()

        await m.delete()

        user = client.get_user(user_id)
        dm_channel = user.dm_channel
        if dm_channel is None:
            await user.create_dm()
            dm_channel = user.dm_channel

        embed = create_embed(
            "!Programs Command Created Successfully", "", "light_green"
        )
        add_field(embed, "Programs", programs, True)

        await dm_channel.send(embed=embed)

        return True

    return False