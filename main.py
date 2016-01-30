#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urwid

import ui_infobar
from ui_infobar import InfoBar
import ui_chanwidget
from ui_chanwidget import ChanWidget
import ui_msgwidget
from ui_msgwidget import MessageWidget

palette = [('title', 'bold,yellow', 'dark blue'),
        ('hint', 'bold,yellow', 'dark blue'),
        ('msg', 'white', 'dark red'),
        ('chan', 'black', 'white')]

def exit_on_q (key):
    if key in ('q','Q'):
        raise urwid.ExitMainLoop

# Barre de titre
title_bar = InfoBar ("ncTelegram v0.1", 
                     style='title', bar_align='top', text_align='center')

# Barre de commandes
hint_bar = InfoBar ("Quit (Q)", 
                    style='hint', bar_align='bottom', text_align='left')

# Liste des chans
chan_widget = ChanWidget ();
chan_widget.updateChanList ([["ÉCALIR", "Que de conchiage !"], 
                            ["ÉCLAIR","Pour les choses sérieuses"]]);

# Liste des messages
msg_widget = MessageWidget ();
msg_widget.updateMsgList ([["flo","Eh, c'est pas mal !"],
                          ["seb","Bof, pas terrible…"]])


# Arrangements finaux
main_columns = urwid.Columns ([('weight', 1, chan_widget),
                               ('weight', 5, msg_widget)])
main_pile = urwid.Pile([title_bar, main_columns, hint_bar])

main_loop = urwid.MainLoop((main_pile), palette, unhandled_input=exit_on_q)
main_loop.screen.set_terminal_properties(colors=256)
main_loop.run ()

# vim: ai ts=4 sw=4 et sts=4
