## BOT PARA RESTART AUTOMÁTICO DO CLIENT DE IMPRESSÕES

import discord
from discord import app_commands
import psutil
import sys
import os
from dotenv import load_dotenv
import logging
import subprocess
from pathlib import Path

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN is None:
    print('Token vazio. Preencher com um token')
    exit(1)

CLIENTE = os.getenv('CLIENTE')
if CLIENTE is None:
    print('Cliente não configurado no .env')
    exit(1)
else:
    CLIENTE = CLIENTE.lower()

CAMINHO_EXE = os.getenv('CAMINHO_EXE')
if CAMINHO_EXE is None:
    print('Variável "CAMINHO_EXE" não preenchida no env. Favor corrigir.')
    exit(1)

PROCESSO = os.getenv('PROCESSO')
if PROCESSO is None:
    print('Variável "PROCESSO" não preenchida no env. Favor corrigir.')
    exit(1)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
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
        print(f'Bot iniciado com sucesso. Log em: debug.log')

    async def on_message(self, message):
        # Ignora mensagens do próprio bot
        if message.author == self.user:
            return
            
        message.content = message.content.lower()
        
        # Verifica permissões
        if isinstance(message.author, discord.Member):
            is_admin = any(role.name == "admin" for role in message.author.roles)
        else:
            is_admin = False
            
        has_restart = "restart" in message.content
        has_cliente = CLIENTE in message.content if CLIENTE else False
        bot_grafana = "Grafana" in message.author.name
        
        if bot_grafana and has_restart and has_cliente or is_admin and has_restart and has_cliente:
            await message.channel.send(f'Verificando processo {PROCESSO}...')
            
            processo_encontrado = False
            
            # Procura o processo
            for proc in psutil.process_iter(['name']):
                try:
                    if PROCESSO.lower() in proc.info['name'].lower():
                        processo_encontrado = True
                        proc.kill()
                        await message.channel.send(f'✅ Processo {PROCESSO} encontrado e finalizado. Cliente = {CLIENTE}')
                        break

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if processo_encontrado:
                subprocess.Popen([CAMINHO_EXE])
                await message.channel.send(f'Processo reiniciado')
            else:
                subprocess.Popen([CAMINHO_EXE])
                await message.channel.send(f'Processo iniciado.')
        else:
            # Responde apenas se o comando foi tentado mas sem permissão
            if "restart" in message.content:
                await message.channel.send("❌ Você não tem permissão para usar este comando.")

bot = botImpressoes()
bot.run(TOKEN)