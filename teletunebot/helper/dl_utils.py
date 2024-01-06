from pathlib import Path
from aiofiles import open as async_open
from teletunebot.config import download_path
from typing import Union
import aiohttp
import re
import mimetypes

import os


def path_create(path: Union[str,Path]):
    if not os.path.exists(path):
        os.makedirs(path)

async def download_url(uri: str,path: Union[str,Path]=download_path,file_name: str=None) -> Path:
    path_create(path)
    async with aiohttp.ClientSession() as session:
        async with session.get(url=uri) as response:
            if not file_name:
                if content_disposition := response.headers.get(
                    'content_disposition'
                ):
                    file_name = re.findall(r'filename=(.+)',content_disposition)[0]
                else:
                    file_name = uri.split('/')[-1]

            ext = re.findall(r'\.(\w+)$',file_name)
            if not ext:
                mime = response.headers.get('content-type')
                ext = mimetypes.guess_extension(mime)
                if ext is None:
                    ext = ''
                file_name += ext

            file_path = Path(path) / file_name

            async with async_open(file_path,'wb') as dl:
                while True:
                    chunk = await response.content.read(512*1024)
                    if not chunk:
                        break
                    await dl.write(chunk)

    return file_path