#!/usr/bin/python3
# -*- coding: utf-8 -*-


import time

import urwid

from ui_infobar import InfoBar
from ui_chanwidget import ChanWidget
from ui_msgwidget import MessageWidget
from ui_msgsendwidget import MessageSendWidget
from msg_receiver import MessageReceiver 
from pytg import Telegram



class Telegram_ui:
    def __init__(self):
        self.start_Telegram()
        palette = [('title', 'bold,yellow', 'dark blue'),
                   ('hint', 'bold,yellow', 'dark blue'),
                   ('msg', 'white', 'dark red'),
                   ('chan', 'black', 'white')]

        self.current_chan = []        

        # Barre de titre
        title_bar = InfoBar("ncTelegram v0.01", 
                             style='title', bar_align='top', text_align='center')

        # Barre de commandes
        hint_bar = InfoBar("Quit(Q)", 
                            style='hint', bar_align='bottom', text_align='left')

        # Liste des chans
        self.chan_widget = ChanWidget(self);
    
        # Liste des messages
        self.msg_widget = MessageWidget(self);

        # Envoie de messages
        self.msg_send_widget = MessageSendWidget(self);

        # Thread du dump de messages
        self.msg_dump = MessageReceiver(self)
        self.msg_dump.daemon = True
        self.msg_dump.start()

        # Panneau droit
        right_side = urwid.Pile([self.msg_widget, (1, self.msg_send_widget)])

        # Arrangements finaux
        main_columns = urwid.Columns([('weight', 1, self.chan_widget),
                                      ('weight', 5, right_side)])
        main_pile = urwid.Pile([(1, title_bar), main_columns, (1, hint_bar)])

        self.main_loop = urwid.MainLoop((main_pile), palette, unhandled_input=self.exit_on_q)
        self.main_loop.screen.set_terminal_properties(colors=256)
        self.main_loop.run()


    def start_Telegram(self):
        # Liaison avec telegram-cli
        self.tg = Telegram(telegram="/usr/bin/telegram-cli",
                      pubkey_file="/etc/telegram-cli/server.pub")
        self.receiver = self.tg.receiver
        self.sender = self.tg.sender
        self.receiver.start()
        time.sleep(2)  # FIX ME


    def stop_Telegram(self):
        self.tg.stopCLI()


    def exit(self):
        self.stop_Telegram()
        raise urwid.ExitMainLoop


    def exit_on_q(self, key):
        if key in('q','Q'):
            self.exit()



Telegram_ui()


# vim: ai ts=4 sw=4 et sts=4
