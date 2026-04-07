import discord
from discord import app_commands
import psutil
import subprocess
import os
from dotenv import load_dotenv
import logging

PROCESSO = 'discord'
CAMINHO_EXE = r'C:\imp_direta_cf\ImpressaoDireta.exe'

#CARREGANDO O ENV
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENTE = os.getenv('CLIENTE').lower()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[logging.FileHandler('debug.log', encoding='utf-8'), logging.StreamHandler()]
)

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
        if message.author == self.user:
            return
            
        content_lower = message.content.lower()
        
        if (any(role.name == "admin" for role in message.author.roles) and 
            "restart" in content_lower and 
            CLIENTE == "semar"):
            for proc in psutil.process_iter(['name']):
                if PROCESSO in proc.info['name'].lower():
                    try:
                        proc.kill() 
                        await message.channel.send(f'Processo do serviço de impressão morto. Cliente: {CLIENTE}')
                        subprocess.Popen([CAMINHO_EXE], shell=True)
                        await message.channel.send(f'Processo do serviço de impressão reiniciado.')
                    except Exception as e:
                        await message.channel.send(f'Erro: {e}')

bot = botImpressoes()
bot.run(TOKEN)