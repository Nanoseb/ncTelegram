# -*- coding: utf-8 -*-


from pytg import Telegram
tg = Telegram(
            telegram="/usr/bin/telegram-cli",
                pubkey_file="/etc/telegram-cli/server.pub")
receiver = tg.receiver
sender = tg.sender


list_contact = sender.execute_function("contacts_list")

print(list_contact)
sender.send_msg("Seb", "Test !!!")


