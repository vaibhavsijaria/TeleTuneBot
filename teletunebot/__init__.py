from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient
from teletunebot.config import api_id,api_hash,bot_token,mongo_uri

plugins = dict(root='teletunebot/plugins')

bot = Client(name='TeleTuneBot',
             api_id=api_id,
             api_hash=api_hash,
             bot_token=bot_token, plugins=plugins)

clientdb = AsyncIOMotorClient(mongo_uri)