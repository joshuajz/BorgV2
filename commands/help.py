import discord
from methods.embed import create_embed, add_field

# TODO: Add !programs_add


async def help_command(ctx, client: discord.Client):
    """!help"""
    embed = create_embed("Help", "", "orange")

    add_field(embed, "!help", "Provides a list of all commands.", True)
    add_field(
        embed, "!roles", "Provides a list of the roles a user can add with !add.", True
    )
    add_field(
        embed,
        "!role",
        "Allows the user to add a role.  Example: !add Member.",
        True,
    )
    add_field(
        embed,
        "!create_role",
        "Allows an administrator to add a new role to be used with !role.",
        True,
    )
    add_field(
        embed,
        "!remove_role",
        "Allows an administrator to remove a role used with !role.",
        True,
    )
    add_field(
        embed,
        "!create_command",
        "Allows an administrator to create a custom command",
        True,
    )
    add_field(
        embed,
        "!remove_command",
        "Allows an administrator to remove a custom command",
        True,
    )
    add_field(embed, "!commands", "Provides a list of all of the custom commands", True)
    add_field(
        embed,
        "!programs_setup {channel}",
        "Allows an administrator to setup the !programs.",
        True,
    )
    add_field(embed, "!programs", "Allows someone to look up a user's commands.", True)
    add_field(embed, "!programs_add", "Allows a user to add their !programs.", True)
    add_field(embed, "!programs_remove", "Allows you to remove your programs.", True)
    await ctx.channel.send(embed=embed)
