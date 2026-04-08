import discord
from discord import app_commands
import psutil
import sys
import os
from dotenv import load_dotenv
import logging
import subprocess

PROCESSO = 'javaw'
CAMINHO_EXE = r'C:\Users\suporte\Desktop\impressaodireta\ImpressaoDireta.exe'

# IMPORTANDO VARIAVEL "TOKEN" DO ENV
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN is None:
    print('Token vazio. Preencher com um token')
    exit(1)

# IMPORTANDO VARIAVEL "CLIENTE" DO ENV
CLIENTE = os.getenv('CLIENTE')
if CLIENTE is None:
    print('Cliente não configurado no .env')
    CLIENTE = ''
else:
    CLIENTE = CLIENTE.lower()

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

    # Verifica se todos os requisitos estão preenchidos
    if is_admin or (bot_grafana and has_restart and has_cliente):
        await message.channel.send(f'🔍 Verificando processo {PROCESSO}...')
        
        processo_encontrado = False
        processos_killados = 0
        
        # Procura e mata todos os processos existentes
        for proc in psutil.process_iter(['name']):
            try:
                if PROCESSO.lower() in proc.info['name'].lower():
                    processo_encontrado = True
                    proc.kill()
                    processos_killados += 1
                    logging.info(f'Processo {PROCESSO} finalizado. PID: {proc.pid}')
                    await message.channel.send(f'⚠️ Processo {PROCESSO} encontrado e finalizado.')
                    
            except psutil.NoSuchProcess:
                # Processo desapareceu durante a tentativa, ignora
                continue
            except (psutil.AccessDenied, psutil.ZombieProcess) as e:
                logging.warning(f'Não foi possível finalizar processo: {e}')
                continue
        
        # Se encontrou e matou, avisa quantos
        if processos_killados > 0:
            await message.channel.send(f'✅ {processos_killados} instância(s) finalizada(s).')
        
        # SEMPRE tenta iniciar o processo (se estava rodando, reinicia; se não, apenas inicia)
        try:
            await message.channel.send(f'🚀 Iniciando/Reiniciando o processo {PROCESSO}...')
            subprocess.Popen([CAMINHO_EXE])
            await message.channel.send(f'✅ Processo iniciado com sucesso! Cliente = {CLIENTE}')
            logging.info(f'Processo {PROCESSO} iniciado via comando')
            
        except Exception as e:
            await message.channel.send(f'❌ Erro ao iniciar o processo: {e}')
            logging.error(f'Erro ao iniciar {CAMINHO_EXE}: {e}')
            
    else:
        # Responde apenas se o comando foi tentado mas sem permissão
        if "restart" in message.content:
            await message.channel.send("❌ Você não tem permissão para usar este comando.")

bot = botImpressoes()
bot.run(TOKEN)