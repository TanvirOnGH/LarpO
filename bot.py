import sys
import nextcord
from nextcord.ext import commands
from config import ConfigReader
from utils import ChatLogger, time_now
from ollama import OllamaClient

# TODO: Config to change activity
config_reader = ConfigReader(filename="config.ini")
TOKEN = config_reader.get_setting("Bot", "token")
PREFIX = config_reader.get_setting("Bot", "prefix", default="!")
DESCRIPTION = config_reader.get_setting("Bot", "description")
STATUS = config_reader.get_setting("Bot", "status")
STATUS_CHANNEL_ID = config_reader.get_setting(
    "Server", "status_channel_id", as_type=int
)
CONVERSATION_CHANNEL_ID = config_reader.get_setting(
    "Server", "conversation_channel_id", as_type=int
)

# Initialize Ollama client
ollama_client = OllamaClient()

# Initialize ChatLogger
logger = ChatLogger()

# Initialize Discord bot
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, description=DESCRIPTION)

# Valid STATUS values: dnd, idle, online, invisible
status_enum_member = getattr(nextcord.Status, STATUS, None)


# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    if status_enum_member is not None:
        await bot.change_presence(status=status_enum_member)
    else:
        print(f"Invalid status: {STATUS}", file=sys.stderr)

    channel = bot.get_channel(STATUS_CHANNEL_ID)
    if channel:
        latency = round(bot.latency * 1000)  # Convert to milliseconds
        await channel.send(f"[{time_now()}] **{latency}ms**")


# Event: Message received
@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return

    response = ollama_client.model_response(message.content, stream=False, raw=False)

    # TODO: Handle prompt token
    if message.channel.id == CONVERSATION_CHANNEL_ID:
        async with message.channel.typing():
            response = ollama_client.model_response(
                message.content, stream=False, raw=False
            )

        await message.reply(response)
        logger.log_to_database(message.author.name, message.content, response)


# Run the bot
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
finally:
    print("Bot is Offline!")
