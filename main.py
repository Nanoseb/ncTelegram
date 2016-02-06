#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from gi.repository import Notify

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
        palette = [('status_bar', 'bold,white', 'dark gray'),
                   ('date', 'light green', ''),
                   ('hour', 'dark gray',''),
                   ('reversed', 'standout', ''),
                   ('cur_chan', 'light green,bold', ''),
                   ('dark red','dark red',''),
                   ('dark green', 'dark green',''),
                   ('brown','brown',''),
                   ('dark blue','dark blue',''),
                   ('dark magenta','dark magenta',''),
                   ('dark cyan','dark cyan',''),
                   ('light gray','light gray',''),
                   ('dark gray','dark gray',''),
                   ('light red','light red',''),
                   ('light green', 'light green',''),
                   ('light blue', 'light blue',''),
                   ('light magenta','light magenta',''),
                   ('light cyan','light cyan',''),
                   ('white', 'white',''),]

        # Notification
        self.notif = True
        if self.notif:
            Notify.init("ncTelegram")
            self.image = os.getcwd()+'/t_logo.png'
        self.me = self.sender.get_self()

        self.current_chan = []        
        self.total_msg_waiting = 0
        self.print_title()

        # Barre de titre
        title_bar = InfoBar("ncTelegram v0.01", 
                             style='status_bar', bar_align='top', text_align='center')


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
        self.right_side = urwid.Pile([self.msg_widget,  (2, self.msg_send_widget)])
        
        vert_separator = urwid.AttrMap(urwid.Filler(urwid.Columns([])), 'status_bar')
        
        # Arrangements finaux
        self.main_columns = urwid.Columns([('weight', 1, self.chan_widget),
                                        (1, vert_separator),
                                      ('weight', 5, self.right_side)])
        main_pile = urwid.Pile([(1, title_bar), self.main_columns,])

        self.main_loop = urwid.MainLoop((main_pile), palette, unhandled_input=self.exit_on_q)
        self.main_loop.screen.set_terminal_properties(colors=256)
        self.main_loop.run()

    def display_notif(self, msg):
        if self.notif:
            text = msg['text']
            
            try:
                sender = msg['from']['first_name']
            except:
                sender = msg['receiver']['name'] + " : " + msg['sender']['first_name']

            Notify.Notification.new('', '<b>' + sender + '</b>\n' + text, self.image).show()

                

    
    def print_title(self):
        if self.total_msg_waiting == 0:
            sys.stdout.write("\x1b]2;ncTelegram\x07")
        else:
            sys.stdout.write("\x1b]2;ncTelegram [" + str(self.total_msg_waiting) + "]\x07")

    def start_Telegram(self):
        # Liaison avec telegram-cli
        self.tg = Telegram(telegram="/usr/bin/telegram-cli",
                      pubkey_file="/etc/telegram-cli/server.pub")
        self.receiver = self.tg.receiver
        self.sender = self.tg.sender
        self.receiver.start()


    def stop_Telegram(self):
        self.tg.stopCLI()


    def exit(self):
        Notify.uninit()
        self.stop_Telegram()
        raise urwid.ExitMainLoop


    def exit_on_q(self, key):
        if key in('q','Q'):
            self.exit()



Telegram_ui()


# vim: ai ts=4 sw=4 et sts=4
