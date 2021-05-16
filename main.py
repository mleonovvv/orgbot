# bot.py
import os
import re
import discord
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

@tasks.loop(seconds=50.0)
async def slow_count():
    res = db.all()
    cur_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    for r in res:
        if r["date"] == cur_date:
            msg = ''
            print(f'cur_date: {cur_date}')
            r = db.get(where("date") == cur_date)
            print(f'Alert for id: {r["author_id"]}')
            channel = client.get_channel(r["channel_id"])
            if r["author_id"]:
                for i in r["author_id"]:
                    msg = msg + f'<@{i}> '

                await channel.send(f'{msg} {r["game_name"]}!')
            else:
                msg = f'Сейчас могли бы играть в {r["game_name"]}'
                await channel.send(f'{msg} {r["game_name"]}!')
        else:
            print("Nothing to alert")

@client.event
async def on_ready():
    slow_count.start()
    print(f'{client.user} has connected to Discord!')

async def responce(message, game_name, author_name_list, date):
    names = ''''''
    c = 1

    for author_name in author_name_list:

        names = names + f'''{c} - {author_name}\n'''
        c += 1

    if author_name_list:
        response = f'сегодня {game_name} в {date.strftime("%H:%M")}. Подписались: \n{names}'
        res = await message.channel.send(response)
    else:
        response = f'сегодня хотели {game_name} в {date.strftime("%H:%M")}, но все отписались'
        res = await message.channel.send(response)

    print(f'game_name: {game_name}, date: {date}')

    r = db.update(
        {"message_id": res.id},
        where('game_name') == game_name and where('date') == date.strftime("%Y-%m-%d %H:%M")
    )

    print(f'update: {r}')

    emojis = ['➕', '➖']

    for emoji in emojis:
        await res.add_reaction(emoji)

async def subscribe(reaction, game_name, game_date, user):

    print(f"game_name: {game_name}")
    print(f"game_date: {game_date}")

    res = db.get(where('message_id') == reaction.message.id)
    
    if user.name in res["author_name"]:
        response = f'Пользователь {user.name} уже подписан'
        res = await reaction.message.channel.send(response)
    else:
        add_author_name_list = res["author_name"]
        add_author_name_list.append(user.name)
        add_author_id_list = res["author_id"]
        add_author_id_list.append(user.id)
        db.update({"author_name": add_author_name_list}, where('message_id') == reaction.message.id)
        db.update({"author_id": add_author_id_list}, where('message_id') == reaction.message.id)
        date_in_db = datetime.strptime(game_date, "%Y-%m-%d %H:%M")
        cur_date = datetime.now()

        if date_in_db.date() == cur_date.date():
            response = f'Пользователь {user.name} подписан на {game_name} сегодня в {date_in_db.strftime("%H:%M")}'
        else:
            response = f'Пользователь {user.name} подписан на {game_name} в {date_in_db.strftime("%d %b %H:%M")}'

        res = await reaction.message.channel.send(response)

async def unsubscribe(reaction, game_name, game_date, user):
    res = db.get(where('message_id') == reaction.message.id)

    if user.name in res["author_name"]:
        add_author_name_list = res["author_name"]
        add_author_name_list.remove(user.name)
        add_author_id_list = res["author_id"]
        add_author_id_list.remove(user.id)
        db.update({"author_name": add_author_name_list}, where('message_id') == reaction.message.id)
        db.update({"author_id": add_author_id_list}, where('message_id') == reaction.message.id)
        date_in_db = datetime.strptime(game_date, "%Y-%m-%d %H:%M")
        response = f'Пользователь {user.name} отписан от {game_name} в {str(date_in_db)}'
        res = await reaction.message.channel.send(response)        
    else:
        response = f'Пользователь {user.name} не подписан на {game_name}' 
        res = await reaction.message.channel.send(response)
        
@client.event
async def on_message(message):

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
        print(f'message.channel.id: {message.channel.id}')

        # Insert a row of data
        db.insert({
            'message_id': "",
            'channel_id': message.channel.id,
            'game_name': game_name, 
            'author_id': author_id_list,
            'author_name': author_name_list,
            'date': date.strftime("%Y-%m-%d %H:%M")
            })

        await responce(message, game_name, author_name_list, date)
 
    # STATUS

    if message.content == '!четам':

        res = db.all()
        print(f"If. rs_db = {res}")

        if res:
            for r in res:
                game_name = r["game_name"]
                author_name = r["author_name"]
                date = r["date"]
                date_in_db = datetime.strptime(r["date"], "%Y-%m-%d %H:%M")
                cur_date = datetime.now()
                
                if date_in_db.date() == cur_date.date():
                    await responce(message, game_name, author_name, date_in_db)
                else:
                    print("Else")
                    response = f'На сегодня игорей нет'
                    res = await message.channel.send(response)
                    print(f'сообщенее отправлено - {res.id}')

        else:
            print("Else")
            response = f'База расписаний пустая'
            res = await message.channel.send(response)
            print(f'сообщенее отправлено - {res.id}')

        #conn.close()

    pattern_rm = re.compile("^(!rm)\s(.*)")
    match_result_rm = re.match(pattern_rm, message.content)

    # RM 

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

@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    print(f'reaction.message.id = {reaction.message.id}')
     #print(f'MESSAGE_ID = {MESSAGE_ID}')
    res = db.all()
    messages_list = []
    for i in res:
        messages_list.append(i["message_id"])

    if reaction.message.id in messages_list:

        if reaction.emoji == "➕":
            res = db.get(where('message_id') == reaction.message.id)
            game_name = res["game_name"]
            game_date = res["date"]
            #response = f'{user} - подписался'
            await subscribe(reaction, game_name, game_date, user)
            #await reaction.message.channel.send(response)
        else:
            print(f"reaction.emoji not equal ➕: {reaction.emoji}")

        if reaction.emoji == "➖":
            res = db.get(where('message_id') == reaction.message.id)
            game_name = res["game_name"]
            game_date = res["date"]
            await unsubscribe(reaction, game_name, game_date, user)
            print(f"{user} - отписался")
            #response = f'{user} - отписался'
            #await reaction.message.channel.send(response)
        else:
            print("Else minus")

client.run(TOKEN)
