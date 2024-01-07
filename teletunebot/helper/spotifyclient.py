import spotipy
from spotipy.oauth2 import SpotifyOAuth
from teletunebot.helper.mongodb import get_collection
from teletunebot.config import spotify_client_id,spotify_client_secret,spotify_redirect_uri
from typing import Union
from pyrogram.types import (Message, InlineQuery,
                             InlineQueryResultArticle, InputTextMessageContent)

scope = ['user-read-playback-state','user-modify-playback-state']

auth_manager = SpotifyOAuth(client_id=spotify_client_id,
                            client_secret=spotify_client_secret,
                            redirect_uri=spotify_redirect_uri,
                            open_browser=False,
                            scope=scope)

async def spot_client(user: Union[Message,InlineQuery] = None,user_id: int = None) -> spotipy.Spotify:
    
    collection = get_collection('teletunebot','spotcreds')
    userid = user.from_user.id if user else user_id
    refresh_token = await collection.find_one({'_id':userid})
    if refresh_token:
        refresh_token = refresh_token['refresh_token']
    else:
        if isinstance(user,InlineQuery):
            await user.answer(
                results=[
                    InlineQueryResultArticle(title='Link you spotify account in dm!',
                                            input_message_content=InputTextMessageContent("Link you spotify account using /register in dm!"))
                ]
            )
            return None
        elif isinstance(user,Message):
            await user.reply('Link you spotify account using /register')
            return None

    access_token = auth_manager.refresh_access_token(refresh_token=refresh_token)
    return spotipy.Spotify(
        auth=access_token['access_token'], auth_manager=auth_manager
    )