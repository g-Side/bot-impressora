## BOT PARA RESTART AUTOMÁTICO DO CLIENT DE IMPRESSÕES

import discord
from discord import app_commands
import psutil
import subprocess

PROCESSO = 'discord'
CAMINHO_EXE = r'C:\Users\suporte\Desktop\impressaodireta\ImpressaoDireta.exe'

class botImpressoes(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!',
            intents=intents
        )
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f'O bot {self.user} foi iniciado com sucesso.')

    async def on_message(self, message):
        message.content = (message.content.lower())
        if any(role.name == "admin" for role in message.author.roles) and "restart" in message.content:
            for proc in psutil.process_iter(['pid', 'name']):
                if PROCESSO in proc.info['name'].lower():
                    try:
                        proc.kill() 
                        await message.channel.send(f'Processo {PROCESSO} morto.')
                        subprocess.Popen([CAMINHO_EXE], shell=True)
                        await message.channel.send(f'Processo {PROCESSO} reiniciado.')
                    except Exception as e:
                        await message.channel.send(f'Erro: {e}')
bot = botImpressoes()

bot.run('MTQ3NjIyMDYzNTkzMDY5MzY1Mg.G5l2Ko.ELg7KbgaLpAeW-rmFIAi8KsUVbWW7YjmMXB50Y')




