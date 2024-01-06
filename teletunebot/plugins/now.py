import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Union

from pyrogram import Client,filters,enums
from pyrogram.types import (Message, InlineQuery, InlineQueryResultCachedPhoto,InlineKeyboardButton,
                            InlineQueryResultArticle, InputTextMessageContent,InlineKeyboardMarkup)

from teletunebot.helper.mongodb import get_collection
from teletunebot.helper.make_img import make_img
from teletunebot.helper.filters import sudo_users_filter,spotify_now_filter,spotify_auth_filter
from teletunebot.config import (spotify_client_id,spotify_client_secret,
                              spotify_redirect_uri,log_channel)


scope = ['user-read-playback-state']

auth_manager = SpotifyOAuth(client_id=spotify_client_id,
                            client_secret=spotify_client_secret,
                            redirect_uri=spotify_redirect_uri,
                            open_browser=False,
                            scope=scope)

@Client.on_message(filters.command('register'))
async def spot_reg(client: Client,msg: Message):
    auth_url = auth_manager.get_authorize_url()
    await msg.reply(f'Connect to your spotify using [this url]({auth_url}) and paste the redirected url below')

@Client.on_message(filters.command('disconnect'))
async def spot_unreg(client: Client, msg: Message):
    collection = get_collection('teletunebot','spotcreds')
    collection.delete_one({'_id':msg.from_user.id})
    await msg.reply('Disconnect successfully!')

@Client.on_message(spotify_auth_filter)
async def spot_auth(client: Client, msg:Message):
    code = auth_manager.parse_response_code(msg.text)
    token = auth_manager.get_access_token(code)

    collection = get_collection('teletunebot','spotcreds')
    collection.insert_one({'_id':msg.from_user.id,'refresh_token':token['refresh_token']})
    await msg.reply('Connected successfully!')
    

@Client.on_message(filters.command('now'))
async def spotify_now(client,message: Message):
    await message.reply_chat_action(action=enums.ChatAction.TYPING)
    sp = await spot_client(message)
    if sp:
        playback = await get_playback(sp)
        if not playback:
            await message.reply("You are not playing anything!")
        else:
            await make_img(playback,message.chat.username)
            await message.reply_photo(photo='downloads/status.jpg',reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    'Listen on Spotify',url=playback['track_url']
                )]
            ]))
        os.remove('downloads/status.jpg')

@Client.on_inline_query(spotify_now_filter)
async def spotify_now_inline(client: Client,query: InlineQuery):
    sp = await spot_client(query)
    if sp:
        playback = await get_playback(sp)
        if not playback:
            await query.answer(
                results=[
                    InlineQueryResultArticle(title='Not Playing anything',
                                            input_message_content=InputTextMessageContent("You are not playing anything!"))
                ]
            )
        else:    
            await make_img(playback,query.from_user.username)
            photo = await client.send_photo(chat_id=log_channel,photo='downloads/status.jpg',)
            await photo.delete()
            await query.answer(
                results=[
                    InlineQueryResultCachedPhoto(photo_file_id=photo.photo.file_id,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                    'Listen on Spotify',url=playback['track_url']
                    )]]))],
                is_personal=True,
                cache_time=10
            )
            os.remove('downloads/status.jpg')

async def spot_client(user: Union[Message,InlineQuery]):
    
    collection = get_collection('teletunebot','spotcreds')
    refresh_token = await collection.find_one({'_id':user.from_user.id})
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

async def get_playback(sp: spotipy.Spotify):
    playback = sp.current_playback()
    # print(playback['item']['external_urls']['spotify'])
    if not playback:
        return None
    return {'track_name': playback['item']['name'],
            'artist_name': playback['item']['artists'][0]['name'],
            'album_name': playback['item']['album']['name'],
            'cover_url': playback['item']['album']['images'][0]['url'],
            'progress_ms': playback['progress_ms'],
            'duration_ms': playback['item']['duration_ms'],
            'track_url': playback['item']['external_urls']['spotify']}