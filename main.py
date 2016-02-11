#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time

import urwid
from pytg import Telegram
try:
    from gi.repository import Notify
    NOTIF = True
except:
    NOTIF = False

from ui_infobar import InfoBar
from ui_chanwidget import ChanWidget
from ui_msgwidget import MessageWidget
from ui_msgsendwidget import MessageSendWidget
from msg_receiver import MessageReceiver


PATH_TELEGRAM = "/usr/bin/telegram-cli"
PATH_PUBKEY = "/etc/telegram-cli/server.pub"


class Telegram_ui:
    def __init__(self):

        global NOTIF, PATH_TELEGRAM, PATH_PUBKEY
        self.lock_receiver = True
        self.start_Telegram()

        palette = [('status_bar', 'bold,white', 'dark gray'),
                   ('date', 'light green', ''),
                   ('hour', 'dark gray', ''),
                   ('separator', 'dark gray', ''),
                   ('reversed', 'standout', ''),
                   ('cur_chan', 'light green', ''),
                   ('dark red', 'dark red', ''),
                   ('dark green', 'dark green', ''),
                   ('brown', 'brown', ''),
                   ('dark blue', 'dark blue', ''),
                   ('dark magenta', 'dark magenta', ''),
                   ('dark cyan', 'dark cyan', ''),
                   ('light gray', 'light gray', ''),
                   ('dark gray', 'dark gray', ''),
                   ('light red', 'light red', ''),
                   ('light green', 'light green', ''),
                   ('light blue', 'light blue', ''),
                   ('light magenta', 'light magenta', ''),
                   ('light cyan', 'light cyan', ''),
                   ('white', 'white', ''),]

        # Notification
        if NOTIF:
            Notify.init("ncTelegram")
            self.image = os.path.dirname(os.path.abspath(__file__))+'/t_logo.png'

        self.current_chan = []

        # Barre de titre à voir si c'est vraiment utile
        #title_bar = InfoBar("ncTelegram v0.01",
        #                    style='status_bar', bar_align='top', text_align='center')

        # Cache des messages
        self.msg_cache = {}

        # Liste des chans
        self.chan_widget = ChanWidget(self)

        # barre de titre
        self.print_title()

        # Liste des messages
        self.msg_widget = MessageWidget(self)

        # Envoie de messages
        self.msg_send_widget = MessageSendWidget(self)

        # Thread du dump de messages
        self.msg_dump = MessageReceiver(self)
        self.msg_dump.daemon = True
        self.msg_dump.start()

        # Panneau droit
        self.right_side = urwid.Pile([self.msg_widget, (2, self.msg_send_widget)])

        vert_separator = urwid.AttrMap(urwid.Filler(urwid.Columns([])), 'status_bar')

        # Arrangements finaux
        self.main_columns = urwid.Columns([('weight', 1, self.chan_widget),
                                           (1, vert_separator),
                                           ('weight', 5, self.right_side)])
        #main_pile = urwid.Pile([(1, title_bar), self.main_columns,])

        self.main_loop = urwid.MainLoop((self.main_columns), palette, unhandled_input=self.unhandle_key)
        self.main_loop.screen.set_terminal_properties(colors=16)
        self.me = self.sender.get_self()
        self.lock_receiver = False
        self.main_loop.run()


    def display_notif(self, msg):
        if NOTIF:
            text = msg['text']

            try:
                sender = msg['peer']['first_name']
            except:
                sender = msg['receiver']['name'] + ": " + msg['sender']['first_name']

            Notify.Notification.new('', '<b>' + sender + '</b>\n' + text, self.image).show()


    def print_title(self):
        total_msg_waiting = sum(self.chan_widget.msg_chan.values())
        if total_msg_waiting == 0:
            sys.stdout.write("\x1b]2;ncTelegram\x07")
        else:
            sys.stdout.write("\x1b]2;ncTelegram (" + str(total_msg_waiting) + ")\x07")


    def start_Telegram(self):
        # Liaison avec telegram-cli
        self.tg = Telegram(telegram=PATH_TELEGRAM,
                           pubkey_file=PATH_PUBKEY)
        self.receiver = self.tg.receiver
        self.sender = self.tg.sender
        self.receiver.start()


    def stop_Telegram(self):
        #self.tg.stopCLI()
        self.sender.terminate()
        self.receiver.stop()


    def exit(self):
        sys.stdout.write("\x1b]2;\x07")
        Notify.uninit()
        self.stop_Telegram()
        raise urwid.ExitMainLoop


    def unhandle_key(self, key):
        if key in('q', 'Q'):
            self.exit()

        elif key == 'esc':
            self.msg_widget.draw_separator()


if __name__ == "__main__":
    Telegram_ui()


# vim: ai ts=4 sw=4 et sts=4
