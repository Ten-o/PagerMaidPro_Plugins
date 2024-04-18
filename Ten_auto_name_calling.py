# -*- coding: utf-8 -*-
"""
@author: 𝓣𝓮𝓷 𝓸'𝓬𝓵𝓸𝓬𝓴
@software: PyCharm
@file: Ten_auto_name_calling.py
@time: 2024/1/9 17:18
"""

""" PagerMaid module Ten_auto_name_calling """
from pagermaid.enums import Client, Message
from pagermaid.listener import listener, _lock
from pagermaid.single_utils import sqlite
import random
import requests
import subprocess


def install_dependencies(packages):
    try:
        subprocess.check_call(['pip', '--version'])
        pip_command = 'pip'
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call(['pip3', '--version'])
            pip_command = 'pip3'
        except subprocess.CalledProcessError:
            print("Error: Neither pip nor pip3 found. Please install pip or pip3.")
            return

    subprocess.call([pip_command, 'install'] + packages)

try:
    import aiosqlite
    import asyncio
except Exception as e:
    packages_to_install = ['aiosqlite', 'asyncio']
    install_dependencies(packages_to_install)
    print(e)

emote_dict_cache = {}

async def load_emote_dict():
    global emote_dict_cache
    try:
        conn = await aiosqlite.connect('./data.db')
        cursor = await conn.cursor()
        await cursor.execute('SELECT * FROM main')
        emote_dict_cache = await cursor.fetchall()
        await conn.close()
    except Exception as e:
        emote_dict_cache = requests.post('https://api.ouklc.com/issue_list').json()
    print(f'加载了 {len(emote_dict_cache)} 条数据')



@listener(outgoing=True, ignore_edited=True, incoming=True)
async def em(message: Message, bot: Client):
    if not emote_dict_cache:
        await load_emote_dict()
    if message.from_user and message.from_user.id:
        emote_dict = sqlite.get(f"Auto_MR.{message.from_user.id}")
        if emote_dict:
            try:
                for i in range(int(emote_dict[f'{message.from_user.id}']['number'])):
                    random_row = random.choice(emote_dict_cache)[1]
                    first_key = next(iter(emote_dict))  # 获取字典中的第一个键
                    mention_text = f'<a href="tg://user?id={first_key}">@{emote_dict[first_key]["name"]}</a> {random_row}'
                    await bot.send_message(message.chat.id, mention_text)
                    await asyncio.sleep(0.3)
            except Exception as e:
                print(e)

@listener(is_plugin=False, outgoing=True, command="m", description='\n列出所有已经设置了自动发送表情符号的用户')
async def M_R(message: Message, bot: Client):
    if not emote_dict_cache:
        await load_emote_dict()
    random_row = random.choice(emote_dict_cache)[1]
    await message.edit(f"{random_row}")

@listener(is_plugin=False, outgoing=True, command="list_auto_m", description='\n列出所有已经设置了自动发送表情符号的用户')
async def list_Auto(message: Message, bot: Client):
    emote_dict = {}
    for key, value in sqlite.items():
        if key.startswith("Auto_MR."):
            emote_dict[key.split(".")[1]] = value
    output = "已经设置了自动骂人的用户有：\n"
    for key, data in emote_dict.items():
        name = data[f'{key}']['name']
        number = data[f'{key}']['number']
        output += f"  {key}: {name}  {number}\n"
    await message.edit(f"{output}")
    await asyncio.sleep(10)
    await bot.delete_messages(message.chat.id, message.id)


@listener(is_plugin=False, outgoing=True, command="set_auto_m", description='\n添加自动点击emo_m')
async def set_Auto(message: Message, bot: Client):
    number = message.arguments
    if not number.isdigit():
        number = 1
    if not number:
        number = 1
    if not sqlite.get(f"Auto_MR.{message.reply_to_message.from_user.id}"):
        id_emote = {
            f'{message.reply_to_message.from_user.id}': {'name': f'{message.reply_to_message.from_user.first_name}', "number": number
                                                         },
        }
        sqlite[f"Auto_MR.{message.reply_to_message.from_user.id}"] = id_emote
        await message.edit(f"✅ 已对{message.reply_to_message.from_user.first_name}启动自动骂人")
    else:
        sqlite.pop(f"Auto_MR.{message.reply_to_message.from_user.id}")
        id_emote = {
            f'{message.reply_to_message.from_user.id}': {'name': f'{message.reply_to_message.from_user.first_name}',
                                                        "number": number},
        }
        sqlite[f"Auto_MR.{message.reply_to_message.from_user.id}"] = id_emote
        await message.edit(f"✅ 已替换{message.reply_to_message.from_user.first_name}自动骂人")
    await asyncio.sleep(5)
    await bot.delete_messages(message.chat.id, message.id)


@listener(is_plugin=False, outgoing=True, command="del_auto_m",
          description='\n删除自动骂人')
async def del_Auto(message: Message, bot: Client):
    if message.arguments:
        id = str(message.arguments)
    else:
        id = str(message.reply_to_message.from_user.id)
    if not id:
        return await message.edit("出错了呜呜呜 ~ 没有成功获取到消息 ID！")

    if sqlite.get(f"Auto_MR.{id}"):
        sqlite.pop(f"Auto_MR.{id}")
        await message.edit(f"✅ {id} 自动骂人已经成功删除！")
    else:
        await message.edit(f"❌ {id} 没有找到对应的自动点信息！")
    await asyncio.sleep(5)
    await bot.delete_messages(message.chat.id, message.id)
