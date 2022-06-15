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

    @arg_botcmd("name", type=str)
    @arg_botcmd("--action", type=str, dest="action", default="restart")
    @arg_botcmd("--worker", type=str, dest="worker", default="'all'")
    def restart_all_worker(self, msg, action, worker, name):
        if msg.frm.id not in os.getenv ("TELEGRAM_ID_ADMIN"):
            return "У вас недостаточно прав для выполнения команды\n" \
                   "Обратитесь к администратору"
        """
            if you send it /restart_all_worker --action 'restart' --worker 'all' Server-001 or
                           /restart all worker --action 'restart' --worker 'all' Server-001
            --action will be 'restart'
            --worker will be 'all'
            name will be 'Server-001'
            :return: supervisorctl restart all
        """
        return self.__run_command_on_server(msg, name, f"supervisorctl {action} {worker}")

    @staticmethod
    def __run_command_on_server(msg, name, command):
        if msg.frm.id not in os.getenv ("TELEGRAM_ID_ADMIN"):
            return "У вас недостаточно прав для выполнения команды\n" \
                   "Обратитесь к администратору"
        with paramiko.SSHClient() as ssh_client:
            ssh_client.load_system_host_keys()
            ssh_client.connect(
                hostname=SERVERS[name],
                port=22, #65075
                username="root", #errbot_user
                key_filename="/root/.ssh/id_rsa" #/errbot_user/.ssh/id_rsa
            )
            _, stdout, _ = ssh_client.exec_command(command)
            return stdout.read().decode("utf-8")

    @re_botcmd(pattern="^Run command (?P<command>.*?) on server (?P<name>.*?)$")
    def run_command(self, msg, matcher: re.match):
        if msg.frm.id not in os.getenv ("TELEGRAM_ID_ADMIN"):
            return "У вас недостаточно прав для выполнения команды\n" \
                   "Обратитесь к администратору"
        """
            Commands for admin
        """
        return self.__run_command_on_server(
            msg,
            matcher.group("name"),
            matcher.group("command"),
        )

    def callback_message(self, msg: Message):
        if msg.frm.id not in os.getenv ("TELEGRAM_ID_ADMIN"):
            return "У вас недостаточно прав для выполнения команды\n" \
                   "Обратитесь к администратору"
        elif any(trigger in msg.body.lower() for trigger in "root"):
             self.send(msg.frm,
                       "Для выполнения любых команд на сервере используйте конструкцию: \n"
                       "^Run command (?P<command>.*?) on server (?P<name>.*?)$ \n"
                       "(?P<command>.*?) - любая команда\n"
                       "(?P<name>.*?)$ - имя сервера\n"
                       )

    def callback_message(self, msg: Message) -> None:
        if any(trigger in msg.body.lower() for trigger in ["helps"]):
            self.send(msg.frm,
                      "You can use command: \n"
                      "В примере использую имя Asterisk-001, но это может быть любой сервер с астериском \n"
                      "---------------------------------ОБЩИЕ КОМАНДЫ:------------------------------------ \n"
                      "/servers                                          -- Получить сведения о доступных серверах\n"
                      "/ifconfig Asterisk-001                            -- Получить сведения о сетевых интерфейсах\n"
                      "/iptables --view S                                -- Получить сведения о правилах iptables\n"
                      "/free mem --view h                                -- Получить сведения об оперативной памяти (h - в Гб, m - в Мб)\n"
                      "/info disk --view h                               -- Получить сведения о состоянии диска\n"
                     )
        elif any(trigger in msg.body.lower() for trigger in ["команды астериск"]):
            self.send(msg.frm,
                      "You can use command: \n"
                      "В примере использую имя Asterisk-001, но это может быть любой сервер с астериском \n"
                      "---------------------------------ОБЩИЕ КОМАНДЫ:--------------------------------- \n"
                      "/servers\nПолучить сведения о доступных серверах\n"
                      "/ifconfig Asterisk-001\nПолучить сведения о сетевых интерфейсах\n"
                      "/iptables --view S\nПолучить сведения о правилах iptables\n"
                      "/free mem --view h\nПолучить сведения об оперативной памяти (h - в Гб, m - в Мб)\n"
                      "/info disk --view h\nПолучить сведения о состоянии диска\n"
                      )
        elif any(trigger in msg.body.lower() for trigger in "root"):
            self.send(msg.frm,
                      "Для выполнения любых команд на сервере используйте конструкцию: \n"
                      "^Run command (?P<command>.*?) on server (?P<name>.*?)$ \n"
                      "(?P<command>.*?) - любая команда\n"
                      "(?P<name>.*?)$ - имя сервера\n"
                      )
        elif any(trigger in msg.body.lower() for trigger in ["как узнать нагрузку оперативной памяти", "как получить сведения об оперативной памяти"]):
            self.send(msg.frm,
                      "Чтобы получить сведения об оперативной памяти, используйте команду free_mem\n"
                      "Узнать все команды бота - /helps или /commands"
                      )
