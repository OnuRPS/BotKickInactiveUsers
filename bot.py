from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantsRequest, EditBannedRequest
from telethon.tl.types import ChannelParticipantsSearch, ChatBannedRights
import datetime
import asyncio
import os

# Citim datele din variabilele de mediu (setate pe Railway)
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

# Inițializăm clientul Telegram
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def kick_inactive_users():
    async for user in client.iter_participants(GROUP_ID):
        if user.bot or user.deleted:
            continue  # Nu dăm kick la boți sau conturi șterse

        last_seen = user.status.was_online if hasattr(user.status, 'was_online') else None
        if last_seen:
            days_inactive = (datetime.datetime.utcnow() - last_seen).days
            if days_inactive >= 3:
                try:
                    await client(EditBannedRequest(
                        GROUP_ID, user.id, ChatBannedRights(until_date=None, view_messages=True)
                    ))
                    print(f"Kicked user {user.id} for inactivity")
                    await asyncio.sleep(1)  # Pauză pentru a evita rate-limit
                except Exception as e:
                    print(f"Eroare la eliminarea utilizatorului {user.id}: {e}")

async def main():
    while True:
        print("Checking for inactive users...")
        await kick_inactive_users()
        await asyncio.sleep(86400)  # Rulează la fiecare 24 de ore

with client:
    client.loop.run_until_complete(main())
