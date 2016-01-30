#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urwid

palette = [('title', 'bold,yellow', 'dark blue'),
        ('hint', 'bold,yellow', 'dark blue'),
        ('msg', 'white', 'dark red'),
        ('chan', 'black', 'white')]

def exit_on_q (key):
    if key in ('q','Q'):
        raise urwid.ExitMainLoop

# Barre de titre
title_bar = urwid.Text(('title', u"ncTelegram v0.0"),align='center')
title_attr = urwid.AttrMap (title_bar, 'title')
title_filler = urwid.Filler (title_attr, 'top')

# Barre de commandes
hint_bar = urwid.Text(('hint', u"Quit (Q)"),align='left')
hint_attr = urwid.AttrMap (hint_bar, 'hint')
hint_filler = urwid.Filler (hint_attr, 'bottom')

# Liste des chans
#################
chan_title = urwid.Text(('chan', u"Chans!"),align='center')
chan_title_attr = urwid.AttrWrap (chan_title, 'chan')
chan_title_filler = urwid.Filler (chan_title_attr, 'bottom')

chan_connection_list = urwid.Text(('chan', "Chans!"),align='left')
chan_list_attr = urwid.AttrWrap (chan_connection_list, 'chan')
chan_list_filler = urwid.Filler (chan_list_attr, 'middle')

chan_pile = urwid.Pile ([chan_list_filler])

chans = [["ÉCALIR","En voilà du chonchiage !"],
        ["nc-telegram project","En voilà un nom trop long !"]]
for i in chans:
    chan_connection_list.set_text (chan_connection_list.text 
    + u"\n→ " + i[0] + ": " + i[1])

# Liste des messages
#####################
msg_title = urwid.Text(('msg', u"Messages!"),align='center')
msg_title_attr = urwid.AttrWrap (msg_title, 'msg')
msg_title_filler = urwid.Filler (msg_title_attr, 'bottom')

msg_connection_list = urwid.Text(('msg', "Messages!"),align='left')
msg_list_attr = urwid.AttrWrap (msg_connection_list, 'msg')
msg_list_filler = urwid.Filler (msg_list_attr, 'middle')

msg_pile = urwid.Pile ([msg_list_filler])

msgs = [["flo","Eh, c'est pas mal !"],["seb","Bof, pas terrible…"]]
for i in msgs:
    msg_connection_list.set_text (msg_connection_list.text 
    + u"\n→ " + i[0] + ": " + i[1])


# Arrangements finaux
main_columns = urwid.Columns ([('weight', 1, chan_pile),
                               ('weight', 5, msg_pile)])
main_pile = urwid.Pile([title_filler, main_columns, hint_filler])

main_loop = urwid.MainLoop((main_pile), palette, unhandled_input=exit_on_q)
main_loop.screen.set_terminal_properties(colors=256)
main_loop.run ()

# vim: ai ts=4 sw=4 et sts=4
