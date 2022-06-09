import os
import re
import paramiko
from errbot import BotPlugin, botcmd, Message, arg_botcmd, re_botcmd
from dotenv import load_dotenv

load_dotenv()

SERVERS = {
    "Server-001": "1.1.1.1",
    "Server-002": "2.2.2.2",
}

class Commands(BotPlugin):
    @botcmd
    def servers(self, msg: Message, args):
        if args:
            server_ip = SERVERS.get(args)
            if server_ip:
                return server_ip
            return f"Server with name {args} is not know for {msg.frm}"
        return str(SERVERS)

    @botcmd
    def start(self, msg, args):
        if msg.frm.id not in os.getenv ("TELEGRAM_ID_ADMIN"):
            return "У вас недостаточно прав для выполнения команды\n" \
                   "Обратитесь к администратору"
        return "Для начало работы введите следующие *команды*\n" \
               "/commands - узнать все команды бота\n" \
               "Так же можно задать вопросы типа:\n" \
               "как узнать нагрузку оперативной памяти?\n"
