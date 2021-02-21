import discord
from methods.database import database_connection
from methods.embed import add_field, create_embed
import shlex


async def welcome_handling(ctx, client):
    db = await database_connection(ctx.guild.id)

    welcome_info = db["db"].execute("SELECT * FROM welcome").fetchone()

    if welcome_info[2] == 0:
        return

    if welcome_info[0] == None or welcome_info[1] == None:
        return

    message = welcome_info[1]
    channel = welcome_info[0]

    channel = client.get_channel(int(channel))
    await channel.send(message.replace("{{USER}}", ctx.mention))


async def welcome_setup(ctx, client):
    if ctx.author.guild_permissions.administrator != True:
        return

    db = await database_connection(ctx.guild.id)
    content = shlex.split(ctx.content)

    if len(content) != 3:
        embed = create_embed(
            "Welcome_setup", "!welcome_setup {@channel} {description}", "orange"
        )
        add_field(
            embed,
            "@channel",
            "Provide the @ for the channel you want the welcome message to be in.",
            True,
        )
        add_field(
            embed,
            "description",
            'Create a welcome message for your server.  Example: "Welcome {{USER}} to the server!".',
            True,
        )
        add_field(
            embed,
            "Hint",
            "The {{USER}} charchter will be repleaced with the User's @ when they join the server.",
            True,
        )
        await ctx.channel.send(embed=embed)
        return

    channel = content[1][2:-1]
    message = content[2]

    db["db"].execute(
        "UPDATE welcome SET channel = ?, message = ?, enabled = ?",
        (channel, message, True),
    )
    db["con"].commit()

    embed = create_embed("Welcome Message Created Successfully", "", "light_green")
    add_field(embed, "Message", message, True)
    add_field(embed, "Channel", channel, True)
    await ctx.channel.send(embed=embed)


async def welcome_toggle(ctx, client):
    if ctx.author.guild_permissions.administrator != True:
        return

    db = await database_connection(ctx.guild.id)
    content = shlex.split(ctx.content)

    if len(content) != 1:
        embed = create_embed(
            "Welcome Toggle", "Toggles the Welcome message on and off.", "orange"
        )
        await ctx.channel.send(embed=embed)
        return

    welcome_info = list(db["db"].execute("SELECT * FROM WELCOME").fetchone())
    if welcome_info[2] == 0:
        welcome_info[2] = 1
        embed = create_embed("Welcome Message Enabled", "", "light_green")
    else:
        welcome_info[2] = 0
        embed = create_embed("Welcome Message Disabled", "", "red")

    db["db"].execute(
        "UPDATE welcome SET channel = ?, message = ?, enabled = ?",
        (welcome_info[0], welcome_info[1], welcome_info[2]),
    )
    db["con"].commit()

    await ctx.channel.send(embed=embed)
