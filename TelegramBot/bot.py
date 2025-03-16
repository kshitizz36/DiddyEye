import requests
import os
import pytesseract as te
from PIL import Image
import telebot
from telebot import types
from dotenv import load_dotenv
import time

from Backend.app.controllers.model import reliability_model
from Backend.app.controllers.AICheckModel import aiChecker_model
from Backend.app.controllers.heatmap_model import heatmap_creator

load_dotenv()

BOT_TOKEN ="7892871646:AAHBcTKGGJL42RfxMVeyDp3HZCl_g_yT9tw"
bot = telebot.TeleBot(BOT_TOKEN)

# GLOBAL PARAMETERS FOR MODEL
redundancy_threshold = 10
max_search_count = 35
min_source_count = 40
keyword_query_percentage = 0.6
max_sites_in_query = 4
is_singapore_sources = True
from tensorflow.keras.models import load_model

# Fix model loading with absolute path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)  # Get the parent directory
model_path = os.path.join(root_dir, 'Backend', 'MobileNetV2_finetuned_model(0.95 loss 0.11).keras')
model = load_model(model_path)

# This dictionary will store each user's current "mode"
# e.g. user_mode[chat_id] = "reliability" or "ai" or None
user_mode = {}


def call_model(message, user_text, isReliability=True):
    """
    Wrapper function to call either the reliability_model or aiChecker_model
    depending on the isReliability flag.
    """
    if isReliability:
        reliability_model(
            message, user_text, bot,
            redundancy_threshold=redundancy_threshold,
            max_search_count=max_search_count,
            min_source_count=min_source_count,
            max_sites_in_query=max_sites_in_query,
            keyword_query_percentage=keyword_query_percentage,
            is_singapore_sources=is_singapore_sources
        )
    else:
        aiChecker_model(message, user_text, bot)
        if os.path.isfile(user_text):
            try:
                processing_msg = bot.send_message(message.chat.id, "Generating heatmap visualization... Please wait.")

                heatmap_path = heatmap_creator(user_text, model)  # heatmap generation

                with open(heatmap_path, 'rb') as heatmap_img:
                    bot.send_photo(message.chat.id, heatmap_img,
                                   caption="Heatmap visualization showing AI detection regions")

                bot.delete_message(message.chat.id, processing_msg.message_id)

            except Exception as e:
                bot.send_message(message.chat.id, f"Error generating heatmap: {str(e)}")
    send_again(message)


def send_usage(message, command, usage):
    bot.reply_to(message, f"Usage: /{command} {usage}")


@bot.message_handler(commands=['set_min_source_count'])
def set_min_source_count_cmd(message):
    global min_source_count
    parts = message.text.split()
    if len(parts) != 2:
        send_usage(message, "set_min_source_count", "<integer>")
        return
    try:
        value = int(parts[1])
        min_source_count = value
        bot.reply_to(message, f"min_source_count set to {value}.")
    except ValueError:
        bot.reply_to(message, "Please provide a valid integer.")


@bot.message_handler(commands=['set_is_singapore_sources'])
def set_is_singapore_sources_cmd(message):
    global is_singapore_sources
    parts = message.text.split()
    if len(parts) != 2:
        send_usage(message, "set_is_singapore_sources", "<true/false>")
        return
    value_str = parts[1].lower()
    if value_str in ["true", "1", "yes"]:
        is_singapore_sources = True
        bot.reply_to(message, "is_singapore_sources set to True.")
    elif value_str in ["false", "0", "no"]:
        is_singapore_sources = False
        bot.reply_to(message, "is_singapore_sources set to False.")
    else:
        bot.reply_to(message, "Please provide a valid boolean value: true or false.")


@bot.message_handler(commands=['view_parameters'])
def view_parameters_cmd(message):
    reply = (
        f"Minimum Source Count before Evaluation : {min_source_count}\n"
        f"Singapore Sources Enabled? : {is_singapore_sources}\n"
    )
    bot.reply_to(message, reply)


@bot.message_handler(commands=['reset_parameters'])
def reset_parameters_cmd(message):
    global redundancy_threshold, max_search_count, min_source_count, max_sites_in_query, keyword_query_percentage, is_singapore_sources
    min_source_count = 40
    is_singapore_sources = True
    bot.reply_to(message, "Resetting parameters to defaults...")
    view_parameters_cmd(message)


# Dictionary to store last start timestamp for each user
last_start_time = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global last_start_time
    chat_id = message.chat.id
    now = time.time()

    # If we've sent /start in the last 3 seconds, ignore this one.
    if chat_id in last_start_time and (now - last_start_time[chat_id] < 2):
        return

    last_start_time[chat_id] = now

    welcome_text = (
        "Hello, I'm DiddyEye!\n\n"
        "I can verify reliability of claims or check if an image is AI-generated. 🕵️ \n\n"
        "Choose one of the options below or set my parameters of the bot with the /help command!\n\n"
        "*Tip: For Checking Text Reliability, when checking information not related to Singapore, results will be more accurate if you disable Singapore sources through the help menu.*\n\n"
        "Welcome to DiddyEye!"
    )

    # Create a custom inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=1)
    reliability_btn = types.InlineKeyboardButton("Check Text Reliability 💡", callback_data="reliability_mode")
    ai_btn = types.InlineKeyboardButton("Detect AI Image 🤖", callback_data="ai_mode")
    end_btn = types.InlineKeyboardButton("End Conversation", callback_data="end_convo")
    markup.add(reliability_btn, ai_btn, end_btn)

    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="Markdown")
    user_mode[chat_id] = None


def send_again(message):
    again_text = (
        "Enter a claim to check its reliability or an image to check if it is AI generated. 🕵️ \n\n"
        "Choose one of the options below or set my parameters of the bot with the /help command!\n\n"
        "Type /start to see your options again! 😁"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    reliability_btn = types.InlineKeyboardButton("Check Text Reliability 💡", callback_data="reliability_mode")
    ai_btn = types.InlineKeyboardButton("Detect AI Image 🤖", callback_data="ai_mode")
    end_btn = types.InlineKeyboardButton("End Conversation", callback_data="end_convo")
    markup.add(reliability_btn, ai_btn, end_btn)

    bot.send_message(
        message.chat.id,
        again_text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    # Initialize user mode to None
    user_mode[message.chat.id] = None



@bot.message_handler(commands=['help'])
def send_commands(message):
    """
    Sends help information with available commands as interactive buttons
    """
    # Create keyboard markup
    markup = types.InlineKeyboardMarkup(row_width=1)

    # Create prompt buttons that will ask for parameter values when clicked
    btn_min_source = types.InlineKeyboardButton(
        text="Set Minimum Sources Count 🎲",
        callback_data="prompt_min_source"
    )

    btn_singapore_sources = types.InlineKeyboardButton(
        text="Disable/Enable Singapore Sources 🇸🇬",
        callback_data="toggle_singapore_sources"
    )

    # Direct execution buttons
    btn_view_params = types.InlineKeyboardButton(
        text="View Current Parameters",
        callback_data="exec_view_parameters"
    )

    btn_reset_params = types.InlineKeyboardButton(
        text="Reset Parameters to Default",
        callback_data="exec_reset_parameters"
    )

    # Add buttons to markup in sections
    markup.add(btn_min_source, btn_singapore_sources, btn_view_params, btn_reset_params)

    # Send message with the inline keyboard
    bot.send_message(
        message.chat.id,
        "<b>Help Menu - Select a Command:</b>\nClick a button to execute or configure a parameter:",
        reply_markup=markup,
        parse_mode="HTML"
    )

    # Initialize user mode to None
    user_mode[message.chat.id] = None


# Add this callback handler to process button clicks
@bot.callback_query_handler(func=lambda call: True)
def callback_handle_command(call):
    """
    Handle callback from all inline keyboard buttons
    """
    global redundancy_threshold, max_search_count, min_source_count, max_sites_in_query, keyword_query_percentage, is_singapore_sources

    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Handle welcome menu callbacks
    if call.data == "reliability_mode":
        user_mode[chat_id] = "reliability"
        bot.send_message(chat_id, "You selected: Check Claim Reliability! \n\nSend me text or a image to analyse 🔍")

    elif call.data == "ai_mode":
        user_mode[chat_id] = "ai"
        bot.send_message(chat_id, "You selected: Detect AI Image! \n\nPlease send me an image (as a file or photo) 📷")

    elif call.data == "end_convo":
        user_mode[chat_id] = None
        bot.send_message(chat_id, "Thanks for using DiddyEye! 👋\nType /start to begin again.")

    # Handle direct execution commands
    elif call.data == "exec_view_parameters":
        # Execute view parameters directly
        reply = (
            f"min sources before eval     : {min_source_count}\n"
            f"are sources from singapore  : {is_singapore_sources}\n"
        )
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"<b>Current Parameters:</b>\n\n{reply}",
            parse_mode="HTML"
        )

    elif call.data == "exec_reset_parameters":
        # Execute reset parameters directly
        min_source_count = 40
        is_singapore_sources = True

        reply = (
            f"min_source_count         : {min_source_count}\n"
            f"is_singapore_sources     : {is_singapore_sources}\n"
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"<b>Parameters Reset to Defaults:</b>\n\n{reply}",
            parse_mode="HTML"
        )

    # Handle toggle for Singapore sources
    elif call.data == "toggle_singapore_sources":
        is_singapore_sources = not is_singapore_sources

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"<b>Singapore Sources:</b> {'Enabled ✅' if is_singapore_sources else 'Disabled ❌'}\n\nPreference has been updated.",
            parse_mode="HTML"
        )

    # Handle parameter input prompts
    elif call.data == "prompt_min_source":
        # Create input prompt with number buttons
        markup = types.InlineKeyboardMarkup(row_width=5)
        number_buttons = []

        # Create number buttons (10, 20, 30, 40, 50)
        for num in [10, 20, 30, 40, 50]:
            number_buttons.append(types.InlineKeyboardButton(
                text=str(num),
                callback_data=f"set_min_source_{num}"
            ))

        # Add custom input option
        custom_btn = types.InlineKeyboardButton(
            text="Custom Value...",
            callback_data="custom_min_source"
        )

        # Add back button
        back_btn = types.InlineKeyboardButton(
            text="« Back to Help Menu",
            callback_data="back_to_help"
        )

        markup.add(*number_buttons)
        markup.add(custom_btn)
        markup.add(back_btn)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="<b>Select Minimum Source Count:</b>\n\nChoose how many sources to consider before evaluation:",
            reply_markup=markup,
            parse_mode="HTML"
        )

    # Handle setting min source count from buttons
    elif call.data.startswith("set_min_source_"):
        value = int(call.data.split("_")[-1])
        min_source_count = value

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"<b>Minimum Source Count</b> set to: <b>{value}</b>\n\nParameter has been updated successfully.",
            parse_mode="HTML"
        )

    # Handle custom min source count input
    elif call.data == "custom_min_source":
        msg = bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Please enter a minimum source count (integer value).\n\nReply directly to this message with a number.",
            parse_mode="HTML"
        )

        # Register a next step handler to capture the reply
        bot.register_next_step_handler(msg, process_min_source_input)

    # Handle back to help menu
    elif call.data == "back_to_help":
        send_commands(call.message)

    # Answer callback to remove the loading indicator
    bot.answer_callback_query(call.id)


def process_min_source_input(message):
    """Process custom input for minimum source count"""
    global min_source_count
    try:
        value = int(message.text.strip())
        min_source_count = value
        bot.reply_to(message, f"Minimum source count set to {value}.")
    except ValueError:
        bot.reply_to(message, "Please provide a valid integer. Operation cancelled.")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """
    Handle text messages for analysis.
    """
    chat_id = message.chat.id
    text = message.text.strip()

    # If user_mode is reliability, handle it with reliability_model
    if user_mode.get(chat_id) == "reliability":
        call_model(message, text, isReliability=True)
    # If user_mode is ai, we can pass the text to AI checker if it was a link
    elif user_mode.get(chat_id) == "ai":
        # If the user typed a URL to an image, you can handle it here
        # If it's just text, you might want to inform them to send an image.
        bot.reply_to(message, "Please send an image as a file, photo, or a direct image URL for AI detection")
    else:
        # No mode selected
        bot.reply_to(message, "Please choose an option from the /start menu first.")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """
    Downloads the photo from the user.
    If user is in 'reliability' mode, we OCR the image text and call reliability_model.
    If user is in 'ai' mode, we pass the image path or URL to aiChecker_model.
    """
    chat_id = message.chat.id
    if message.photo is None:
        bot.reply_to(message, "No photo detected.")
        return

    file_id = message.photo[-1].file_id  # the highest resolution
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    # Download the image locally
    image_folder = "images"
    os.makedirs(image_folder, exist_ok=True)
    response = requests.get(file_url)
    if response.status_code != 200:
        bot.reply_to(message, "Error downloading the image.")
        return

    file_data = response.content
    local_filename = file_path.split("/")[-1]
    local_path = os.path.join(image_folder, local_filename)
    with open(local_path, "wb") as f:
        f.write(file_data)

    # Check user mode
    mode = user_mode.get(chat_id)
    if mode == "reliability":
        # OCR the image to get text, then run reliability_model
        extracted_text = te.image_to_string(Image.open(local_path))
        call_model(message, extracted_text, isReliability=True)
    elif mode == "ai":
        # For AI detection, we likely want to pass the *file path* or *URL* to aiChecker_model
        # Depending on how your aiChecker_model is implemented, you can pass the local path or the file_url.
        # Example: passing the local path
        call_model(message, local_path, isReliability=False)
    else:
        bot.reply_to(message, "Please select a mode first by clicking a button or type /start.")


def start_bot():
    import time
    time.sleep(5)
    print("Bot is polling...")
    bot.polling()