# bot.py
import os
import sqlite3
import re
import discord
import random
from datetime import datetime, timedelta, time
from dotenv import load_dotenv
from discord.ext import tasks, commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

discord.Intents.reactions = True

MESSAGE_DICT = {
    '': {
        "game_id": ""
    }
}

t = "2021-04-25 17:01:10"

@tasks.loop(seconds=1.0)
async def slow_count():
    print(slow_count.current_loop)

    conn = sqlite3.connect('./bot.db')
    
    cursor = conn.execute('select users,datetime from main')
    
    for i in cursor:
        print(i)
        #t = i[1]
        t = "2021-04-25 17:06:15"
        users = i[0]



    print(t)

    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    if datetime.now().strftime("%Y-%m-%d %H:%M:%S") == t:
        print(f"Пора! {users}")
        channel = client.get_channel(835802932456325240)
        await channel.send('<@693168468702265477>  пора!')

    conn.close()

slow_count.start()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    global MESSAGE_DICT
    if message.author == client.user:
        return

    print(message.author)

    brooklyn_99_quotes = [
        'Нет',
        'НЕТ!!',
    ]

    if message.content == 'го в овервоч':

        if message.author != 'cyber#5940':
            await message.channel.send('cyber, перелогинься')

        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)

    pattern_add = re.compile("^(!add)\s(.*)\s(.*)")
    match_result_add = re.match(pattern_add, message.content)

    if match_result_add:
        
        conn = sqlite3.connect('./bot.db')

        # Create table
        # conn.execute('''create table if not exists main
        #     (
        #     id INTEGER PRIMARY KEY AUTOINCREMENT, 
        #     name text,
        #     users text,
        #     datetime datetime
        #     )'''
        # )
        print(message)
        name = match_result_add.groups()[1]
        time = match_result_add.groups()[2]
        print(f'message.author - {message.author}')
        author = str(message.author.id)

        t = datetime.today().strftime('%Y-%m-%d') + "/" + time

        date = datetime.strptime(t, '%Y-%m-%d/%H:%M')

        values = (name, author, date)
        print(f'values - {values}')

        # Insert a row of data
        res = conn.execute('insert into main values (null,?,?,?)', values)
        print(f'res - {res}')
        conn.commit()

        for row in res:
            print(row)
            response = f'{row[0]} - добавлен'
            await message.channel.send(response)

        # Save (commit) the changes
        conn.close()

    if message.content == '!четам':
        conn = sqlite3.connect('./bot.db')
        start_time = datetime.strftime(datetime.now(), "%Y-%m-%d") + " 00:00:00"
        end_time = datetime.strftime(datetime.now(), "%Y-%m-%d") + " 23:59:59"
        t = (start_time, end_time)
        res_db = conn.execute('select * from main where datetime >= ? and datetime <= ?', t)
        print(f"If. rs_db = {res_db}")

        if res_db:
            for row in res_db:                              
                print(f'row {row}')
                t = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                t1 = datetime.strftime(t, "%H:%M")

                row_id = row[0]
                game_name = row[1]
                user = row[2]

                response = f'({row_id})-сегодня {game_name} в {t1}. Подписались: {user}'
                res = await message.channel.send(response)

                emojis = ['➕', '➖']

                for emoji in emojis:
                    await res.add_reaction(emoji)

                print(f'сообщенее отправлено - {res.id}')
                MESSAGE_DICT.update({res.id: {"game_id": row[0]}})
        else:
            print("Else")
            response = f'На сегодня игорей нет'
            res = await message.channel.send(response)
            print(f'сообщенее отправлено - {res.id}')

        conn.close()

    pattern_rm = re.compile("^(!rm)\s(.*)")
    match_result_rm = re.match(pattern_rm, message.content)

    if match_result_rm:

        print(f"got !rm")

        game_id = match_result_rm.groups()[1]

        t = (game_id)

        conn = sqlite3.connect('./bot.db')
        print(f"delete id {t}")
        res = conn.execute('delete from main where id = ?', t)
        print(res)
        if res:
            response = f'{t} - удален'
            await message.channel.send(response)
        else:
            response = f'ничего не удалено'
            await message.channel.send(response)
        conn.commit()

        conn.close()

#    if user.bot:
#        return



# @client.event
# async def on_raw_reaction_add(payload): 
#     print(payload.emoji.name)
#     if payload.emoji.name == "➕" and payload.message_id == message_id:
#         print(f"{payload.member.name} - подписался")
#         #await client.add_roles(user, Role)

def subscribe(row_id, user_id):
    conn = sqlite3.connect('./bot.db')

    t = (row_id["game_id"],)

    print(t)

    cursor = conn.execute('select users from main where id = ?', t)

    user_from_db = cursor.fetchone()[0]

    users = (f'{user} {user_from_db}', row_id["game_id"])

    print(users)

    conn.execute('update main set users = ? where id = ?', users)
    conn.commit()
    conn.close()
    #user = cursor.fetchone()[0]

    print(f'user from DB = {user}')

@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    

    print(f'reaction.message.id = {reaction.message.id}')
    #print(f'MESSAGE_ID = {MESSAGE_ID}')

    if reaction.emoji == "➕" and reaction.message.id in MESSAGE_DICT.keys():
        print(f"{user} - подписался")
        print(f"game_id - {MESSAGE_DICT[reaction.message.id]}")
        game_id = MESSAGE_DICT[reaction.message.id]
        user_id = user.id
        #response = f'{user} - подписался'
        subscribe(game_id, user, user_id)
        #await reaction.message.channel.send(response)
    else:
        print("Else plus")

    if reaction.emoji == "➖" and reaction.message.id in MESSAGE_DICT.keys():
        print(f"{user} - отписался")
        #response = f'{user} - отписался'
        #await reaction.message.channel.send(response)
    else:
        print("Else minus")

client.run(TOKEN)
