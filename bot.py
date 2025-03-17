from telethon import TelegramClient
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import os
import asyncio

# ✅ Environment variables from Railway
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

# ✅ Initialize the Telegram Client
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def has_ever_written(user_id):
    """ Directly check if the user has ever written a message in the group. """
    async for message in client.iter_messages(GROUP_ID, from_user=user_id, limit=1):
        return True  # ✅ User has written at least one message
    return False  # ❌ User has never written anything

async def warn_and_check_user(user):
    """ Send a warning message and wait 5 minutes before kicking the user if they don’t write anything. """
    try:
        message = (
            "Hello! I am **PandaKicker**, a bot that removes users who have never written in the PandaBao group. "
            "You are detected as a potential infiltrated bot. If you are a real user, please write a message in the group. "
            "Otherwise, you will be removed in **5 minutes**."
        )
        await client.send_message(user.id, message)
        print(f"📩 Sent warning to {user.id}")

        await asyncio.sleep(300)  # ⏳ Wait 5 minutes

        # Check again if user wrote something
        if not await has_ever_written(user.id):
            try:
                await client(EditBannedRequest(
                    GROUP_ID,
                    user.id,
                    ChatBannedRights(until_date=None, view_messages=True)  # Kick user
                ))
                print(f"✅ Kicked user {user.id} for never writing in the group.")
            except Exception as e:
                print(f"⚠️ Error kicking user {user.id}: {e}")

    except Exception as e:
        print(f"⚠️ Could not send message to {user.id}. They may have private messages disabled.")

async def kick_non_writers():
    """ Check all users and warn/kick those who never wrote in the group. """
    print("🔍 Checking for users who never wrote anything...")

    async for user in client.iter_participants(GROUP_ID):
        if user.deleted:
            # ❌ Immediately kick deleted accounts
            try:
                await client.EditBannedRequest(
                    GROUP_ID,
                    user.id,
                    ChatBannedRights(until_date=None, view_messages=True)
                )
                print(f"🗑️ Removed deleted account: {user.id}")
                continue
            except Exception as e:
                print(f"⚠️ Error removing deleted account {user.id}: {e}")
                continue

        if user.bot or (user.username and user.username.lower().endswith("_bot")):
            continue  # ✅ Ignore trusted bots (e.g., Rose_bot)

        if not await has_ever_written(user.id):
            await warn_and_check_user(user)  # Send warning and check again after 5 minutes

        await asyncio.sleep(1)  # ⏳ Avoid rate limiting (important for large groups)

async def main():
    print("🛠️ PandaKicker is running! Performing full user check...")
    await kick_non_writers()  # ✅ Perform full check
    print("✅ PandaKicker has completed user verification. Stopping process.")

with client:
    client.loop.run_until_complete(main())
