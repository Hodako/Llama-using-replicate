import logging
import requests
import replicate
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tokens
TELEGRAM_BOT_TOKEN = '7347802263:AAFD4mZemj6X08xKHF4Rt0-n9ZXNtd-89Bc'
REPLICATE_API_TOKEN = 'r8_9HMoezEGuZpZI6LwdMqxB7HC8qHpQou1sULy9'
LLAMA_MODEL_VERSION = 'meta/meta-llama-3-8b-instruct'  # Replace with your actual LLaMA model version ID

# Set the Replicate API token
replicate.Client(api_token=REPLICATE_API_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! I am your LLaMA AI chat bot. How can I help you today?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('You can chat with me by sending any message.')

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message and get a response from LLaMA."""
    user_message = update.message.text
    llama_response = await get_llama_response(user_message)
    await update.message.reply_text(llama_response)

async def get_llama_response(message: str) -> str:
    input = {
        "prompt": message,
        "max_new_tokens": 512,
        "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    }
    
    response_text = ""
    try:
        for event in replicate.stream(
            LLAMA_MODEL_VERSION,
            input=input
        ):
            response_text += event
    except Exception as e:
        logger.error('Error with Replicate API: %s', str(e))
        response_text = 'Sorry, there was an error connecting to the AI service.'

    return response_text

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    application.run_polling()

if __name__ == '__main__':
    main()
