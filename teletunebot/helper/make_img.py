from PIL import Image,ImageEnhance,ImageFilter,ImageDraw,ImageFont
from teletunebot.helper.dl_utils import download_url, path_create
import os


def truncate(text:str, max_width, draw, font):
    text_w = draw.textlength(text,font)
    truncated = (text_w > max_width)
    while text_w > max_width:
        text = text[:-1]
        text_w = draw.textlength(text,font)
    return f'{text}..' if truncated else text

def progress(progress_ms,duration_ms):
    return (progress_ms / duration_ms)*325

async def make_img(track: dict,username: str,
                   img_uri: str=None,):
    if not img_uri:
        img_uri = track['cover_url']
    # download cover img and load it in img obj
    file_path = await download_url(img_uri)
    with Image.open(file_path) as img:
        img.load()
    
    os.remove(file_path)
    # making blur background
    background = img.crop((0,195,640,445))
    background = background.resize((600,250))
    background = background.filter(ImageFilter.GaussianBlur(25))
    darken = ImageEnhance.Brightness(background)
    background = darken.enhance(0.9)
    background.paste(img.resize((200,200)),(25,25))

    # defining fonts
    draw = ImageDraw.Draw(background)
    font1 = ImageFont.truetype('assets/fonts/TruenoBold-XYE2.otf',size=25)
    font2 = ImageFont.truetype('assets/fonts/Trueno-wml2.otf',size=20)

    # truncating long text
    track_name = truncate(track['track_name'],310,draw,font1)
    artist_name = truncate(track['artist_name'],310,draw,font2)
    album_name = truncate(track['album_name'],310,draw,font2)

    #Rendering text
    draw.text((250,20),username,(255,255,255),font=font1)
    draw.text((250,115),track_name,(255,255,255),font=font1)

    draw.text((250,60),'is now listening to',(255,255,255),font=font2)
    draw.text((250,150),artist_name,(255,255,255),font=font2)
    draw.text((250,175),album_name,(255,255,255),font=font2)

    #Rendering progress bar
    marker = progress(track['progress_ms'],track['duration_ms'])
    draw.line([(250,215),(250+marker,215)],fill=(255,255,255),width=3)
    draw.line([(250+marker,215),(575,215)],fill=(0,0,0),width=3)

    path_create('downloads')
    background.save('downloads/status.jpg')

    img.close()
    background.close()