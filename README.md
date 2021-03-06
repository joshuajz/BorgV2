# BorgV2

### About the Project
A discord bot with various commands created specificlly for University Applicant servers, but can be used on any discord server.  Some noteable commands include a !programs command, to allow users to display the universities and programs they're applying to.  It also has custom commands that administrators of the server can create to display information.

### Built with
- [Python](https://www.python.org/)
  - [discord.py](https://discordpy.readthedocs.io/en/latest/index.html)
  - [python-dotenv](https://pypi.org/project/python-dotenv/)
  - [sqlite database](https://www.sqlite.org/index.html)
The full list can be found in the requirements.txt file.

### Setting up a testing environment:

1. Clone the repository
```sh
git clone https://github.com/joshuajz/BorgV2
```



2. Install python: [link](https://www.python.org/downloads/)

3. Install the required libraries from requirements.txt (run this in the project's directory)
```sh
pip3 install -r requirements.txt 
```

4. Create a .env file within the main folder.
5. Create a testing bot with the [discord developer portal](https://discord.com/developers/applications)
6. Create a bot for your discord application & invite the testing bot to a test discord server that you've made.  You probably want to give the bot blanket "administrator" permissions while testing.
7. Go into "Bot" tab and copy the token.
8. Within the original project folder, create a .env file.
9. Paste the token into the .env file -> bot_token=TOKEN_HERE
