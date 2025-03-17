from telethon import TelegramClient, events
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

# ✅ Dictionary to track users who joined but didn't write anything
user_activity = {}

@client.on(events.ChatAction)
async def track_new_users(event):
    """ Track when new users join the group """
    if event.user_joined or event.user_added:
        user_id = event.user_id
        if user_id:
            print(f"👀 New user joined: {user_id}")
            user_activity[user_id] = asyncio.get_event_loop().time()  # Save the join time
            
            # Wait 5 minutes (for testing, in production it will be 3 days)
            await asyncio.sleep(300)

            # If the user hasn't written anything, kick them
            if user_id in user_activity:
                try:
                    await client(EditBannedRequest(
                        GROUP_ID,
                        user_id,
                        ChatBannedRights(until_date=None, view_messages=True)  # Kick user
                    ))
                    print(f"❌ Kicked user {user_id} for inactivity.")
                    del user_activity[user_id]  # Remove from tracking
                except Exception as e:
                    print(f"⚠️ Error while kicking user {user_id}: {e}")

@client.on(events.NewMessage(chats=GROUP_ID))
async def track_messages(event):
    """ Mark users as active when they send a message """
    user_id = event.sender_id
    if user_id in user_activity:
        print(f"✅ User {user_id} is active. Removing from kick list.")
        del user_activity[user_id]  # Remove from tracking since they are active

async def main():
    print("🛠️ PandaKicker is running! Monitoring new users...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
