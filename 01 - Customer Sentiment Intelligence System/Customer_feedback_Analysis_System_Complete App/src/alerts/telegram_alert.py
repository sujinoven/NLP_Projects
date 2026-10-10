# Lifecycle stage 9 / Phase 13 — Automated Negative-Review Alerts (Telegram)
import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default Bot Token from BotFather screenshot
DEFAULT_BOT_TOKEN = "8828856402:AAELEWI5uSTIFjFXQ3T557B353npadTzM1A"
DEFAULT_BOT_USERNAME = "Feedback_Analyser_bot"

def get_config():
    """Retrieve current Telegram bot token and chat ID."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", DEFAULT_BOT_TOKEN)
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    
    # Check if local runtime config exists
    config_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "telegram_config.json")
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, "r") as f:
                saved = json.load(f)
                token = saved.get("token", token) or token
                chat_id = saved.get("chat_id", chat_id) or chat_id
        except Exception as e:
            logger.error(f"Error reading telegram_config.json: {e}")
            
    return token, chat_id

def save_config(token: str, chat_id: str):
    """Save Telegram configuration to data/telegram_config.json."""
    config_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "telegram_config.json")
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    import json
    with open(config_file, "w") as f:
        json.dump({"token": token, "chat_id": chat_id}, f, indent=2)

def auto_detect_chat_id():
    """
    Queries Telegram getUpdates endpoint to auto-detect chat_id 
    from the latest message sent to the bot.
    """
    token, _ = get_config()
    if not token:
        return {"success": False, "error": "No Bot Token configured"}

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if not data.get("ok"):
            return {"success": False, "error": f"Telegram API error: {data.get('description')}"}
        
        results = data.get("result", [])
        if not results:
            return {
                "success": False, 
                "error": "No messages found. Please open Telegram, search for @Feedback_Analyser_bot, press /start or send a message, then try again."
            }

        # Find the latest chat ID
        latest_update = results[-1]
        chat = None
        if "message" in latest_update:
            chat = latest_update["message"]["chat"]
        elif "edited_message" in latest_update:
            chat = latest_update["edited_message"]["chat"]
        elif "my_chat_member" in latest_update:
            chat = latest_update["my_chat_member"]["chat"]

        if chat and "id" in chat:
            chat_id = str(chat["id"])
            username = chat.get("username", chat.get("first_name", "User"))
            save_config(token, chat_id)
            return {
                "success": True, 
                "chat_id": chat_id, 
                "user": username,
                "message": f"Successfully detected chat ID for {username}!"
            }
        else:
            return {"success": False, "error": "Could not parse chat ID from Telegram updates."}

    except Exception as e:
        logger.error(f"Failed to auto-detect chat ID: {e}")
        return {"success": False, "error": str(e)}

def send_telegram_message(message: str, override_chat_id: str = None):
    """Sends a raw text message to Telegram."""
    token, chat_id = get_config()
    target_chat_id = override_chat_id or chat_id

    if not target_chat_id:
        # Try auto detecting if chat ID is not set
        detected = auto_detect_chat_id()
        if detected.get("success"):
            target_chat_id = detected.get("chat_id")
        else:
            raise ValueError("Telegram Chat ID is missing. Please message @Feedback_Analyser_bot on Telegram and click 'Auto-Detect Chat ID' in Settings.")

    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(api_url, data=payload, timeout=10)
    
    # Fallback to plain text if Markdown parsing fails
    if not response.ok and "can't parse entities" in response.text:
        payload.pop("parse_mode", None)
        response = requests.post(api_url, data=payload, timeout=10)

    response.raise_for_status()
    return response.json()

def send_negative_alert(review: str, sentiment: str = "negative", confidence: float = None, customer_name: str = None, category: str = None, rating: int = None):
    """
    Builds a structured negative feedback notification and sends it to Telegram.
    Matches Phase 13 requirements of the project.
    """
    conf_str = f" ({confidence*100:.1f}% confidence)" if confidence is not None else ""
    cust_str = f"👤 *Customer*: {customer_name}\n" if customer_name else ""
    cat_str = f"📦 *Category*: {category}\n" if category else ""
    rating_str = f"⭐ *Rating*: {'⭐'*rating if rating else 'N/A'}\n" if rating else ""

    message = (
        "🚨 *NEGATIVE FEEDBACK ALERT!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{cust_str}"
        f"{cat_str}"
        f"{rating_str}"
        f"📊 *Sentiment*: `NEGATIVE`{conf_str}\n\n"
        "📝 *Review Content*:\n"
        f"_{review}_\n\n"
        "⚡ *Action Required*: Please review this customer issue immediately."
    )

    return send_telegram_message(message)

def send_test_alert(override_chat_id: str = None):
    """Sends a test message to verify Telegram bot setup."""
    message = (
        "🤖 *Telegram Bot Connected Successfully!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Your Telegram alert system for `@Feedback_Analyser_bot` is active.\n"
        "You will receive immediate notifications here whenever a negative customer review is submitted."
    )
    return send_telegram_message(message, override_chat_id=override_chat_id)
