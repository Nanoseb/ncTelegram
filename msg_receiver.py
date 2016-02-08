#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time
from pytg.utils import coroutine

class MessageReceiver(threading.Thread):
    def __init__(self, Telegram_ui):
        threading.Thread.__init__(self)
        self.Telegram_ui = Telegram_ui


    def run(self):
        while self.Telegram_ui.lock_receiver:
            time.sleep(1)

        self.Telegram_ui.receiver.message(self.get_dump())


    @coroutine
    def get_dump(self):
        while True:
            msg = (yield)

            current_type = self.Telegram_ui.current_chan['type']
            current_cmd = current_type + "#" + str(self.Telegram_ui.current_chan['id'])

            if msg['event'] == "message":

                # vérifie que le message a été envoyé au chan courant
                current_type = self.Telegram_ui.current_chan['type']
                current_cmd = current_type + "#" + str(self.Telegram_ui.current_chan['id'])

                msg_type = msg['receiver']['type']
                if msg_type == 'user' and not msg['own']:
                    msg_cmd = msg['sender']['cmd']
                else:
                    msg_cmd = msg['receiver']['cmd']

                # si le message est pas pour le chan courant on actualise le nombre de msg non lut
                if msg_cmd == current_cmd:
                    self.Telegram_ui.msg_widget.print_msg(msg)
                else:
                    self.Telegram_ui.chan_widget.add_msg(msg_cmd)


                self.Telegram_ui.chan_widget.update_chan_list()

                # notif on hl
                if 'text' in msg and self.Telegram_ui.me['username'] != '' and \
                            "@" + self.Telegram_ui.me['username'] in msg['text']:
                    self.Telegram_ui.display_notif(msg)

                # On actualise l'affichage
                self.Telegram_ui.main_loop.draw_screen()

            elif msg['event'] == 'online-status' and current_cmd == 'user#'+str(msg['user']['id']):
                when = msg['when']
                status = msg['online']

                self.Telegram_ui.msg_send_widget.update_online(when, status)






# vim: ai ts=4 sw=4 et sts=4
