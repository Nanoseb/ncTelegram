#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import urwid

#import ui_infobar
from ui_infobar import InfoBar
#import ui_chanwidget
from ui_chanwidget import ChanWidget
#import ui_msgwidget
from ui_msgwidget import MessageWidget

from pytg import Telegram

        
# Liaison avec telegram-cli
tg = Telegram(telegram="/usr/bin/telegram-cli",
              pubkey_file="/etc/telegram-cli/server.pub")
receiver = tg.receiver
sender = tg.sender
time.sleep(2)

palette = [('title', 'bold,yellow', 'dark blue'),
        ('hint', 'bold,yellow', 'dark blue'),
        ('msg', 'white', 'dark red'),
        ('chan', 'black', 'white')]

def exit_on_q(key):
    if key in('q','Q'):
        tg.stopCLI()
        raise urwid.ExitMainLoop

def get_dialog_list():
    dict = sender.dialog_list()
    return  [ [name['print_name'],name['type']] for name in dict ][::-1]


# Barre de titre
title_bar = InfoBar("ncTelegram v0.01", 
                     style='title', bar_align='top', text_align='center')

# Barre de commandes
hint_bar = InfoBar("Quit(Q)", 
                    style='hint', bar_align='bottom', text_align='left')

# Liste des chans
chan_widget = ChanWidget();
chan_widget.updateChanList(get_dialog_list());

# Liste des messages
msg_widget = MessageWidget();
msg_widget.updateMsgList([["flo","Eh, c'est pas mal !"],
                          ["seb","Bof, pas terrible…"]])


# Arrangements finaux
main_columns = urwid.Columns([('weight', 1, chan_widget),
                              ('weight', 5, msg_widget)])
main_pile = urwid.Pile([title_bar, main_columns, hint_bar])

main_loop = urwid.MainLoop((main_pile), palette, unhandled_input=exit_on_q)
main_loop.screen.set_terminal_properties(colors=256)
main_loop.run()

# vim: ai ts=4 sw=4 et sts=4
