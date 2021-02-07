import discord
from methods.database import database_connection, settings_location
import shlex
from methods.embed import create_embed, add_field
import yaml

# TODO: Editing

# TODO: Change Programs Add to a CSV


# ! REWRITING programs_add w/ a csv
async def programs_add(ctx, client):
    content_temp = shlex.split(ctx.content)
    if len(content_temp) <= 1:
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

        await ctx.channel.send(embed=embed)
        return

    content = ctx.content.split("!programs_add")[1][1::]

    if content[0:3] == "<@!":
        if ctx.author.guild_permissions.administrator == True:
            user_id = int(content[3:21])

        content = list(content)
        content[0:23] = ""
        content = "".join(content)
    else:
        user_id = int(ctx.author.id)

    content = content.split(",")

    final_content = []
    for c in content:
        c = list(c)
        if c[0] == " ":
            c[0] = ""
        if c[-1] == " ":
            c[-1] = ""
        c = "".join(c)
        final_content.append(c)

    db = await database_connection(ctx.guild.id)

    data = (
        db["db"]
        .execute("SELECT user_id FROM programs WHERE user_id = (?)", (int(user_id),))
        .fetchone()
    )

    if data is not None:
        embed = create_embed(
            "Error",
            "The user already has a !programs associated with them.  First use !programs_remove.",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    with open(await settings_location(ctx.guild.id)) as f:
        l = yaml.safe_load(f)

        mod_channel_id = l["default_commands"]["programs"][6]["channel"]

        if mod_channel_id is None:
            embed = create_embed(
                "Error",
                "The admins have not setup !programs.  Ask them to run !programs_setup.",
                "red",
            )
            await ctx.channel.send(embed=embed)
            return

    mod_channel = ctx.guild.get_channel(int(mod_channel_id))

    embed = create_embed("Verification Required", "", "magenta")

    message_programs = "```\n"
    for program in final_content:
        message_programs += program + "\n"
    message_programs += "```"

    add_field(embed, "User", client.get_user(int(user_id)).mention, False)
    add_field(embed, "Programs", message_programs, True)
    add_field(embed, "List Version", str(final_content), True)

    verify_message = await mod_channel.send(embed=embed)

    emojis = ["✅", "❌"]
    for emoji in emojis:
        await verify_message.add_reaction(emoji)

    embed = create_embed(
        "Successfully Sent to Moderators",
        "Your !programs command has been sent to the administrators of the server for review.  Please sit tight!",
        "light_green",
    )
    add_field(embed, "User", client.get_user(int(user_id)).mention, False)

    add_field(embed, "Programs", message_programs, True)
    await ctx.channel.send(embed=embed)


async def programs_remove(ctx, client):
    content = shlex.split(ctx.content)

    db = await database_connection(ctx.guild.id)
    if len(content) == 1:
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

    print("data", data)

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
    return


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

    user_id = content[1][3:-1]

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

    programs = eval(
        (
            db["db"]
            .execute("SELECT description FROM programs WHERE user_id = (?)", (user_id,))
            .fetchall()[0][0]
        )
    )

    message = "```\n"
    for program in programs:
        temp = program + "\n"
        message += temp
    message += "```"

    embed = create_embed(f"Programs", "", "orange")
    add_field(embed, "User", f"{client.get_user(int(user_id)).mention}", False)
    add_field(embed, "Programs", message, True)

    await ctx.channel.send(embed=embed)


async def programs_setup(ctx, client):
    # TODO: Make sure a user cannot create a new program if they already have one
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

    with open(await settings_location(ctx.guild.id)) as f:
        l = yaml.safe_load(f)

        l["default_commands"]["programs"][5]["setup"] = 1
        l["default_commands"]["programs"][6]["channel"] = channel_id

        with open(await settings_location(ctx.guild.id), "w") as ff:
            yaml.dump(l, ff)

    embed = create_embed("Programs Setup Successfully", "", "light_green")
    add_field(
        embed, "channel", f"{ctx.guild.get_channel(int(channel_id)).mention}", True
    )
    await ctx.channel.send(embed=embed)


async def program_reaction_handling(ctx, client):
    db = await database_connection(ctx.guild_id)
    with open(await settings_location(ctx.guild_id)) as f:
        l = yaml.safe_load(f)

        mod_channel_id = int(l["default_commands"]["programs"][6]["channel"])

    # Programs isn't setup
    if mod_channel_id is None:
        return False

    if ctx.emoji.name == "❌":
        if mod_channel_id == int(ctx.channel_id):
            m = await client.get_channel(ctx.channel_id).fetch_message(ctx.message_id)
            await m.delete()
            return True
    elif ctx.emoji.name == "✅":
        if mod_channel_id != int(ctx.channel_id):
            return False

        message = await client.get_channel(ctx.channel_id).fetch_message(ctx.message_id)

        embeds = message.embeds[0]

        for embed in embeds.fields:
            if embed.name == "List Version":
                programs_raw = embed.value
            elif embed.name == "User":
                user_id = int(embed.value[2:-1])
            elif embed.name == "Programs":
                programs_message = embed.value

        programs_list = eval(programs_raw)

        if programs_list and user_id:
            db["db"].execute(
                "INSERT INTO programs VALUES (?, ?)", (user_id, str(programs_list))
            )
            db["con"].commit()

        await message.delete()

        # Send a DM to the user
        user = client.get_user(user_id)
        dm_channel = user.dm_channel

        if dm_channel is None:
            await user.create_dm()
            dm_channel = user.dm_channel

        embed = create_embed(
            "!Programs Command Created Successfully", "", "light_green"
        )
        add_field(embed, "Programs", programs_message, True)

        await dm_channel.send(embed=embed)

        return True
    else:
        return False