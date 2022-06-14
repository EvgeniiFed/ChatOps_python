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

    @arg_botcmd("name", type=str)
    @arg_botcmd("--view", type=str, dest="view", default="h")
    def free_mem(self, msg, name, view):
        if msg.frm.id not in os.getenv ("TELEGRAM_ID_ADMIN"):
            return "У вас недостаточно прав для выполнения команды\n" \
                   "Обратитесь к администратору"
        """
            if you send it /free_mem --view h Server-001 or /free mem --view h Server-001
            --view will be 'h'
            name will be 'Server-001'
            :return: free -h
        """
        return self.__run_command_on_server(msg, name, f"free -{view}")

    @arg_botcmd("name", type=str)
    @arg_botcmd("--view", type=str, dest="view", default="h")
    def info_disk(self, msg, name, view):
        if msg.frm.id not in os.getenv ("TELEGRAM_ID_ADMIN"):
            return "У вас недостаточно прав для выполнения команды\n" \
                   "Обратитесь к администратору"
        """
            if you send it /info_disk --view h Server-001 or /info disk --view h Server-001
            --view will be 'h'
            name will be 'Server-001'
            :return: df -h
        """
        return self.__run_command_on_server(msg, name, f"df -{view}")
    
    @arg_botcmd("name", type=str)
    @arg_botcmd("--view", type=str, dest="view", default="S")
    def iptables(self, msg, name, view):
        if msg.frm.id not in os.getenv ("TELEGRAM_ID_ADMIN"):
            return "У вас недостаточно прав для выполнения команды\n" \
                   "Обратитесь к администратору"
        """
            if you send it /iptables --view L Server-001 or /info disk --view h Server-001
            --view will be 'L'
            name will be 'Server-001'
            :return: iptables -L
        """
        return self.__run_command_on_server(msg, name, f"iptables -{view}")

    @arg_botcmd("name", type=str)
    def ifconfig(self, msg, name):
        if msg.frm.id not in os.getenv ("TELEGRAM_ID_ADMIN"):
            return "У вас недостаточно прав для выполнения команды\n" \
                   "Обратитесь к администратору"
        """
            if you send it /ifconfig Server-001
            name will be 'Server-001'
            :return: ifconfig
        """
        return self.__run_command_on_server(msg, name, f"ifconfig")
