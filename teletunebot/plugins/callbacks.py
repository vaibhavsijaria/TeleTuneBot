from pyrogram.types import Message, CallbackQuery
from pyrogram import Client 

from teletunebot.helper.spotifyclient import spot_client

@Client.on_callback_query()
async def show_callback(client: Client, callback: CallbackQuery):
    msg_owner = callback.message.reply_to_message.from_user.id if callback.message.reply_to_message else callback.message.chat.id
    if msg_owner != callback.from_user.id:
        await callback.answer('Not Authorized',show_alert=True)
        return
    sp = await spot_client(user_id=msg_owner)
    if callback.data == 'next_track':
        try:
            sp.next_track()
        except:
            await callback.answer('Premium Required')
    elif callback.data == 'prev_track':
        try:
            sp.previous_track()
        except:
            await callback.answer('Premium Required')
    elif callback.data == 'pause':
        try:
            sp.pause_playback()
        except:
            await callback.answer('Premium Required')
    elif callback.data == 'play':
        try:
            sp.start_playback()
        except:
            await callback.answer('Premium Required')
