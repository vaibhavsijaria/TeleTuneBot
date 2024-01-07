from pyrogram.types import InlineKeyboardButton

playback_control = [
        InlineKeyboardButton('⏮Prev',callback_data='prev_track'),
        InlineKeyboardButton('⏸Pause',callback_data='pause'),
        InlineKeyboardButton('Play▶️',callback_data='play'),
        InlineKeyboardButton('Next⏭',callback_data='next_track')
        ]

