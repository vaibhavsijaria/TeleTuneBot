from pyrogram import filters
from pyrogram.types import Message, InlineQuery

from teletunebot.config import sudo_usr, auth_chats

async def spotify_now_inline(_, __, query: InlineQuery):
    """Check if the inline query is 'now'."""
    return query.query == 'now' if query.query else False

async def spotify_auth(_,__,msg: Message):
    return '?code=' in msg.text if msg.text else False

async def sudo_check(_, __, msg: Message):
    """Check if the message is from a sudo user."""
    return msg.from_user.id in sudo_usr if msg.from_user else False

async def auth_check(_, __, msg: Message):
    """Check if the message is from an authorized chat."""
    return msg.chat.id in auth_chats

spotify_auth_filter = filters.create(spotify_auth)
spotify_now_filter = filters.create(spotify_now_inline)
sudo_users_filter = filters.create(sudo_check)
auth_chat_filter = filters.create(auth_check)