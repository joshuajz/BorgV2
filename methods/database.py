import sqlite3
import os
from shutil import copyfile
import discord
import yaml

SERVERS_DIR = f"{os.getcwd()}/servers"
DEFAULT_DIR = os.getcwd()


async def create_filesystem(client: discord.Client):
    """Creates the filesystem

    Args:
        client (discord.Client): Discord client to get the guilds
    """
    # Check to see if there is a "servers" directory
    if os.path.isdir("servers") == False:
        os.makedirs("servers")

    # Open the "servers" directory
    os.chdir(SERVERS_DIR)

    # List of directory
    list_dir = os.listdir()

    for guild in [i for i in client.guilds if str(i.id) not in list_dir]:
        # Create a folder
        os.mkdir(str(guild.id))

    for guild in os.listdir():
        l_dir = os.listdir(guild)

        if "database.db" not in l_dir:
            db_conn = sqlite3.connect(f"{SERVERS_DIR}/{guild}/database.db")
            db = db_conn.cursor()

            db.execute(
                "CREATE TABLE reaction_roles ([role_id] int, [message_id] int, [reaction_id] int, [channel_id] int)"
            )
            """db.execute(
                "CREATE TABLE infractions ([infraction_id] INTEGER PRIMARY KEY, user_id int, type text, reason text, datetime text, time_limit text, active int)"
            )"""
            db.execute("CREATE TABLE normal_roles (role_id int, command text)")
            db.execute(
                "CREATE TABLE custom_commands (command text, output text, image text)"
            )
            db.execute("CREATE TABLE programs (user_id text, description text)")
            db.execute("CREATE TABLE welcome (channel int, message text, enabled bool)")
            db.execute(
                "INSERT INTO welcome VALUES (?, ?, ?)",
                (
                    None,
                    None,
                    False,
                ),
            )

            db_conn.commit()

        if "settings.yml" not in l_dir:
            copyfile(
                f"{DEFAULT_DIR}/settings.yml", f"{SERVERS_DIR}/{guild}/settings.yml"
            )


async def database_connection(guild: int):
    """Creates a database connection with

    Args:
        guild (int): the guild's id

    Returns:
        {'con': sqlite3.Connection, 'db': sqlite3.Cursor}: sqlite3 connection
    """
    db_connection = sqlite3.connect(f"{SERVERS_DIR}/{guild}/database.db")
    db = db_connection.cursor()

    return {"con": db_connection, "db": db}


async def settings_location(guild: int):
    return f"{SERVERS_DIR}/{guild}/settings.yml"
