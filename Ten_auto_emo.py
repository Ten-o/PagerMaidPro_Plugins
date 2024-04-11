""" PagerMaid module Ten_auto_emo """

from pagermaid.enums import Client, Message
from pagermaid.listener import listener, _lock
from pagermaid.single_utils import sqlite
import asyncio
import random

emo = '👍👎❤️🔥🥰👏😁🤔🤯😱🤬😢🎉🤩🙏👌🕊🤡🥱🥴😍🐳❤️‍🔥🌚🌭💯🤣⚡️🍌🏆💔🤨😐🍓🍾💋🖕😈😂😭'

@listener(outgoing=True, ignore_edited=True, incoming=True)
async def em(message: Message, bot: Client):
    if message.from_user and message.from_user.id:
        emote_dict = sqlite.get(f"Auto_emo.{message.from_user.id}")
        if emote_dict:
            emote = emote_dict[f'{message.from_user.id}']['emo']
            if str(emote) == str('re'):
                emote = random.choice(emo)
            if emote:
                try:
                    await bot.send_reaction(message.chat.id, int(message.id), emote)
                except:
                    return



@listener(is_plugin=False, outgoing=True, command="list_auto", description='\n列出所有已经设置了自动发送表情符号的用户')
async def list_Auto(message: Message, bot: Client):
    emote_dict = {}
    for key, value in sqlite.items():
        if key.startswith("Auto_emo."):
            emote_dict[key.split(".")[1]] = value
    output = "已经设置了自动发送表情符号的用户有：\n"
    for key, data in emote_dict.items():
        name = data[f'{key}']['name']
        emo = data[f'{key}']['emo']
        output += f"  {key}: {name} - {emo}\n"
    await message.edit(f"{output}")
    await asyncio.sleep(10)
    await bot.delete_messages(message.chat.id, message.id)

    
@listener(is_plugin=False, outgoing=True, command="set_auto", description='\n添加自动点击emo')
async def set_Auto(message: Message, bot: Client):
    text = message.arguments
    if not text:
        return await message.edit("出错了呜呜呜 ~ 没有成功获取到表情！")
    if not sqlite.get(f"Auto_emo.{message.reply_to_message.from_user.id}"):
        id_emote = {
            f'{message.reply_to_message.from_user.id}': {'name':f'{message.reply_to_message.from_user.first_name}','emo': f'{text}'},
        }
        sqlite[f"Auto_emo.{message.reply_to_message.from_user.id}"] = id_emote
        await message.edit(f"✅ 已对{message.reply_to_message.from_user.first_name}启动自动点{text}")
    else:
        sqlite.pop(f"Auto_emo.{message.reply_to_message.from_user.id}")
        id_emote = {
            f'{message.reply_to_message.from_user.id}': {'name':f'{message.reply_to_message.from_user.first_name}','emo': f'{text}'},
        }
        sqlite[f"Auto_emo.{message.reply_to_message.from_user.id}"] = id_emote
        await message.edit(f"✅ 已替换{message.reply_to_message.from_user.first_name}自动点为{text}")
    await asyncio.sleep(5)
    await bot.delete_messages(message.chat.id, message.id)

    
@listener(is_plugin=False, outgoing=True, command="del_auto",
          description='\n删除自动点击emo')
async def del_Auto(message: Message, bot: Client):
    if message.arguments:
        id = str(message.arguments)
    else:
        id = str(message.reply_to_message.from_user.id)
    if not id:
        return await message.edit("出错了呜呜呜 ~ 没有成功获取到消息 ID！")

    if sqlite.get(f"Auto_emo.{id}"):
        sqlite.pop(f"Auto_emo.{id}")
        await message.edit(f"✅ {id} 自动点已经成功删除！")
    else:
        await message.edit(f"❌ {id} 没有找到对应的自动点信息！")
    await asyncio.sleep(5)
    await bot.delete_messages(message.chat.id, message.id)
