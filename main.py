# bot.py
import os
import sqlite3
import re
import discord
import random
from datetime import datetime, timedelta, time
from dotenv import load_dotenv
from discord.ext import tasks, commands
from tinydb import TinyDB, where


db = TinyDB('db.json')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

discord.Intents.reactions = True
discord.Intents.members = True

MESSAGE_DICT = {
    "message_id": "",
    "game_name": "",
    "date": ""
    }

t = "2021-04-25 17:01:10"

# @tasks.loop(seconds=1.0)
# async def slow_count():
#     #print(slow_count.current_loop)

#     conn = sqlite3.connect('./bot.db')
    
#     cursor = conn.execute('select users,datetime from main')
    
#     for i in cursor:
#         print(i)
#         #t = i[1]
#         t = "2021-04-25 17:22:15"
#         users = i[0]
#         print(t)
#         if t:
#             print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
#             if datetime.now().strftime("%Y-%m-%d %H:%M:%S") == t:
#                 print(f"Пора! {users}")
#                 channel = client.get_channel(835802932456325240)
#                 await channel.send('<@693168468702265477>  пора!')

#     conn.close()




@client.event
async def on_ready():
    # conn = sqlite3.connect('./bot.db')

    # # Create table
    # conn.execute('''create table if not exists main
    #     (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT, 
    #     name text,
    #     users text,
    #     datetime datetime
    #     )'''
    # )
    # conn.commit
    # conn.close

    #slow_count.start()
    print(f'{client.user} has connected to Discord!')


async def responce(message, game_name, author_name_list, date):
    names = ''''''
    c = 1

    for author_name in author_name_list:

        names = names + f'''{c} - {author_name}\n'''
        c += 1

    response = f'сегодня {game_name} в {date.strftime("%H:%M")}. Подписались: \n{names}'
    res = await message.channel.send(response)
    print(res.id)

    MESSAGE_DICT.update({
                        "message_id": res.id,
                        "game_name": game_name,
                        "date": str(date)
                        })

    emojis = ['➕', '➖']

    for emoji in emojis:
        await res.add_reaction(emoji)

async def subscribe(reaction, game_name, game_date, user):

    print(f"game_name: {game_name}")
    print(f"game_date: {game_date}")

    res = db.search(where('game_name') == game_name and where('date') == game_date)
    print(f'res: {res}')
    if user.name in res[0]["author_name"]:
        response = f'Пользователь {user.name} уже подписан'
        res = await reaction.message.channel.send(response)
    else:
        add_author_name_list = res[0]["author_name"]
        add_author_name_list.append(user.name)

        add_author_id_list = res[0]["author_id"]
        add_author_id_list.append(user.id)

        db.update({"author_name": add_author_name_list}, where('game_name') == game_name and where('date') == game_date)
        db.update({"author_id": add_author_id_list}, where('game_name') == game_name and where('date') == game_date)

        date_in_db = datetime.strptime(game_date, "%Y-%m-%d %H:%M:%S")
        cur_date = datetime.now()
        if date_in_db.date() == cur_date.date():
            response = f'Пользователь {user.name} подписан на {game_name} сегодня в {date_in_db.strftime("%H:%M")}'
        else:
            response = f'Пользователь {user.name} подписан на {game_name} в {str(date_in_db)}'
        res = await reaction.message.channel.send(response)

async def unsubscribe(reaction, game_name, game_date, user):

    print(f"game_name: {game_name}")
    print(f"game_date: {game_date}")

    res = db.search(where('game_name') == game_name and where('date') == game_date)
    print(f'res: {res}')
    print(f'author_name-unsubscribe: {res[0]["author_name"]}')

    if user.name in res[0]["author_name"]:
        add_author_name_list = res[0]["author_name"]
        add_author_name_list.remove(user.name)

        add_author_id_list = res[0]["author_id"]
        add_author_id_list.remove(user.id)

        db.update({"author_name": add_author_name_list}, where('game_name') == game_name and where('date') == game_date)
        db.update({"author_id": add_author_id_list}, where('game_name') == game_name and where('date') == game_date)

        date_in_db = datetime.strptime(game_date, "%Y-%m-%d %H:%M:%S")

        response = f'Пользователь {user.name} отписан от {game_name} в {str(date_in_db)}'
        res = await reaction.message.channel.send(response)        

    else:
        response = f'Пользователь {user.name} не подписан на {game_name}'
        res = await reaction.message.channel.send(response)
        
@client.event
async def on_message(message):
    global MESSAGE_DICT
    global MESSAGE_ID
    if message.author == client.user:
        return

    print(message.author)

    pattern_add = re.compile("^(!add)\s(.*)\s(.*)")
    match_result_add = re.match(pattern_add, message.content)

    # ADD

    if match_result_add:
        
        print(message)
        game_name = match_result_add.groups()[1]
        time = match_result_add.groups()[2]
        print(f'message.author - {message.author}')
        author_id_list = []
        author_name_list = []

        author_id_list.append(message.author.id)
        author_name_list.append(message.author.name)

        t = datetime.today().strftime('%Y-%m-%d') + "/" + time

        date = datetime.strptime(t, '%Y-%m-%d/%H:%M')

        # Insert a row of data
        db.insert({
            'game_name': game_name, 
            'author_id': author_id_list,
            'author_name': author_name_list,
            'date': str(date)
            })

        time = str(date.time())
        await responce(message, game_name, author_name_list, date)
 

    if message.content == '!четам':

        res = db.all()
        print(f"If. rs_db = {res}")

        if res:
            for r in res:
                game_name = r["game_name"]
                author_name = r["author_name"]
                date = r["date"]

                date_in_db = datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S")
                cur_date = datetime.now()
                
                if date_in_db.date() == cur_date.date():
                    
                    # MESSAGE_DICT.update({
                    #     "message_id": res.id,
                    #     "game_name": r["game_name"],
                    #     "date": r["date"]
                    #     })

                    await responce(message, game_name, author_name, date_in_db)
                    # time = str(date_in_db.time())
                    # response = f'сегодня {r["game_name"]} в {time}. Подписались: {r["author_name"]}'
                    # res = await message.channel.send(response)
                    # print(res.id)
                    

                    # emojis = ['➕', '➖']

                    # for emoji in emojis:
                    #     await res.add_reaction(emoji)

                else:
                    print("Else")
                    response = f'На сегодня игорей нет'
                    res = await message.channel.send(response)
                    print(f'сообщенее отправлено - {res.id}')


        #         row_id = row[0]
        #         game_name = row[1]
        #         user_id = row[2]

        #         print(f'user_id = {user_id}')
        #         user = client.get_user(693168468702265477)
        #         print(f'user - {user}')

                
        #         res = await message.channel.send(response)

                # emojis = ['➕', '➖']

                # for emoji in emojis:
                #     await res.add_reaction(emoji)

        #         print(f'сообщенее отправлено - {res.id}')
        #         MESSAGE_DICT.update({res.id: {"game_id": row[0]}})
        else:
            print("Else")
            response = f'База расписаний пустая'
            res = await message.channel.send(response)
            print(f'сообщенее отправлено - {res.id}')

        #conn.close()

    pattern_rm = re.compile("^(!rm)\s(.*)")
    match_result_rm = re.match(pattern_rm, message.content)

    # if match_result_rm:

    #     print(f"got !rm")

    #     game_id = match_result_rm.groups()[1]

    #     t = (game_id)

    #     conn = sqlite3.connect('./bot.db')
    #     print(f"delete id {t}")
    #     res = conn.execute('delete from main where id = ?', t)
    #     print(res)
    #     if res:
    #         response = f'{t} - удален'
    #         await message.channel.send(response)
    #     else:
    #         response = f'ничего не удалено'
    #         await message.channel.send(response)
    #     conn.commit()

    #     conn.close()

#    if user.bot:
#        return



# @client.event
# async def on_raw_reaction_add(payload): 
#     print(payload.emoji.name)
#     if payload.emoji.name == "➕" and payload.message_id == message_id:
#         print(f"{payload.member.name} - подписался")
#         #await client.add_roles(user, Role)




@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    print(f'reaction.message.id = {reaction.message.id}')
    #print(f'MESSAGE_ID = {MESSAGE_ID}')

    if reaction.emoji == "➕" and reaction.message.id == MESSAGE_DICT['message_id']:
        print(f'USER {user}')
        print(f'ID {user.id}')
        game_name = MESSAGE_DICT["game_name"]
        game_date = MESSAGE_DICT["date"]
        #response = f'{user} - подписался'
        await subscribe(reaction, game_name, game_date, user)
        #await reaction.message.channel.send(response)
    else:
        print(f"reaction.emoji not equal ➕: {reaction.emoji} or reaction.message.id not equal {reaction.message.id}: {MESSAGE_DICT['message_id']}")

    if reaction.emoji == "➖" and reaction.message.id == MESSAGE_DICT['message_id']:
        game_name = MESSAGE_DICT["game_name"]
        game_date = MESSAGE_DICT["date"]
        await unsubscribe(reaction, game_name, game_date, user)
        print(f"{user} - отписался")
        #response = f'{user} - отписался'
        #await reaction.message.channel.send(response)
    else:
        print("Else minus")

client.run(TOKEN)
