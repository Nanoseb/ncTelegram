#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
from pytg.utils import coroutine

class MessageReceiver(threading.Thread):
    def __init__(self, Telegram_ui):
        threading.Thread.__init__(self)
        self.Telegram_ui = Telegram_ui


    def run(self):
        self.Telegram_ui.receiver.message(self.get_dump())


    @coroutine
    def get_dump(self):
        while True:
            msg = (yield)

            # si c'est un message on l'affiche
            if msg['event'] == "message":

                fichier_log = open('/home/seb/log.tele', "a")
                fichier_log.write(str(msg) + u'\n')
                fichier_log.close()

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


                self.Telegram_ui.chan_widget.updateChanList()
  
                try:
                    if self.Telegram_ui.me['username'] != '' and \
                            "@" + self.Telegram_ui.me['username'] in msg['text']:
                        self.Telegram_ui.display_notif(msg)
                except:
                    """ """

                # On actualise l'affichage 
                self.Telegram_ui.main_loop.draw_screen()
              
# vim: ai ts=4 sw=4 et sts=4
