import logging
import requests
import replicate
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tokens
TELEGRAM_BOT_TOKEN = '7347802263:AAFD4mZemj6X08xKHF4Rt0-n9ZXNtd-89Bc'
REPLICATE_API_TOKEN = 'r8_1uK8tOV2uhXafjb3cMLryj5Ubyi41YF1J8V6K'
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

async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a message to notify the user."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # Notify the user about the error
    await update.message.reply_text('An unexpected error occurred. Please try again later.')

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Add the error handler
    application.add_error_handler(error_handler)

    # Set up webhook
    WEBHOOK_URL = f"https://llama-using-replicate.onrender.com/{TELEGRAM_BOT_TOKEN}"
    application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        webhook_url=WEBHOOK_URL
    )

if __name__ == '__main__':
    main()
