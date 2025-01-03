import tkinter as tk
from tkinter import messagebox, scrolledtext
import discord
from discord.ext import commands
import asyncio
import threading

GUILD_ID = None
names = None
bot = None
root = None
action_to_perform = None
console_output = None
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

async def create_admin(guild, role_name):
    role = discord.utils.get(guild.roles, name=role_name)
    
    if not role:
        role = await guild.create_role(
            name=role_name,
            permissions=discord.Permissions.all(),
            colour=discord.Colour.from_rgb(140, 210, 255)
        )

    await asyncio.sleep(1)
    return role

async def add_admin(guild, role_name, names):
    try:
        role = await create_admin(guild, role_name)
        for user_id in names:
            member = guild.get_member(int(user_id))
            if role and member:
                await member.add_roles(role)
                log_to_console(f"Added {role_name} to {member.name}")
            else:
                log_to_console("유저를 찾을 수 없음")
    except discord.Forbidden as e:
        pass
    except discord.HTTPException as e:
        pass
    except Exception as e:
        pass

async def on_ready():
    global GUILD_ID, action_to_perform
    guild = bot.get_guild(GUILD_ID)
    if guild:
        role_name = 'Admin'
        await add_admin(guild, role_name, names)
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
        global GUILD_ID, TOKEN, names
        try:
            GUILD_ID = int(guild_id_entry.get())
            TOKEN = token_entry.get().strip()
            names = names_entry.get().split(",")
            start_bot(mode='Nuker')
            messagebox.showinfo("Info", "Add Is Starting...")
        except ValueError:
            messagebox.showerror("Error", "Please Enter True 'Bot Token' And 'Server ID' And 'User Id'")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    global root, guild_id_entry, token_entry, names_entry, console_output
    
    root = tk.Tk()
    root.title("Add Admin")
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
    
    tk.Label(root, text="User Id", font=("Arial", 18), fg='purple', bg='black').pack(pady=(15, 5))
    entry_frame = tk.Frame(root, bg='purple', bd=1, relief='solid')
    entry_frame.pack(pady=(5, 20), padx=20, fill='x')
    names_entry = tk.Entry(entry_frame, font=("Arial", 14), bg='black', fg='purple', borderwidth=0, justify='center', width=25)
    names_entry.pack(padx=3, pady=3, fill='x', expand=True)

    button_frame = tk.Frame(root, bg='black')
    button_frame.pack(pady=20)

    nuker_button = tk.Button(button_frame, text="Add", command=on_nuker_button_click, bg='purple', fg='red', font=("Arial", 14), borderwidth=2, relief='solid', highlightbackground='purple', highlightcolor='purple', width=8, height=1)
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