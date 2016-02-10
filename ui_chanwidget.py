#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urwid
import time

class NewButton(urwid.Button):
    def __init__(self, caption, callback, arg):
        super(NewButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback, arg)
        self._w = urwid.AttrMap(urwid.SelectableIcon(caption, 1),
                                None, focus_map='status_bar')

# Le widget utilise pour afficher la liste des chans
class ChanWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.chans = []
        self.updateLocked = False
        self.Telegram_ui = Telegram_ui
        self.msg_chan = {}
        self.update_chan_list()

    # Mettre a jour la liste des chans
    def update_chan_list(self):
        while self.updateLocked:
            time.sleep(0.1)
        self.updateLocked = True

        # Réécriture de la liste, pour actualiser le chan courant
        self.chan_list = urwid.SimpleFocusListWalker([urwid.AttrMap(urwid.Text("Chan list:"), 'status_bar')])
        super().__init__(self.chan_list)

        # list de dictionnaire contenant les chans
        self.chans = None
        while self.chans is None:
            try:
                self.chans = self.Telegram_ui.sender.dialog_list()
            except:
                time.sleep(1)
                pass


        if self.Telegram_ui.current_chan == []:
            self.Telegram_ui.current_chan = self.chans[-1]

        pos = self.focus_position

        # Construction de la liste de chan
        for i in self.chans[::-1]:
            print_name = i['print_name']

            cmd = i['type'] + "#" + str(i['id'])

            label = print_name.replace('_', ' ')

            if i['type'] == 'user':
                label = "➜  " + label
            else:
                label = "➜➜ " + label

            if cmd in self.msg_chan:
                label = label + ' [' + str(self.msg_chan[cmd]) + ']'

            if print_name == self.Telegram_ui.current_chan['print_name']:
                button = NewButton(('cur_chan', label), self.chan_change, print_name)
                current_pos = pos + 1
            else:
                button = NewButton(label, self.chan_change, print_name)

            self.chan_list.insert(pos +1, button)
            pos = pos + 1


        self.focus_position = current_pos
        self.updateLocked = False



    def add_msg(self, cmd):
        """ incrémentation des messages non lut
        """
        if cmd in self.msg_chan:
            self.msg_chan[cmd] = self.msg_chan[cmd] + 1
        else:
            self.msg_chan[cmd] = 1

        self.Telegram_ui.print_title()



    def chan_change(self, button, print_name):

        for i in self.chans:
            if i['print_name'] == print_name:
                self.Telegram_ui.current_chan = i

        current_cmd = self.Telegram_ui.current_chan['type'] + "#" + str(self.Telegram_ui.current_chan['id'])

        # suppression des messages non lut pour le nouveau chan
        if current_cmd in self.msg_chan:
            del self.msg_chan[current_cmd]
            self.Telegram_ui.print_title()

        self.Telegram_ui.msg_send_widget.update_send_widget()
        self.Telegram_ui.msg_widget.get_history()

        #Appel pour actualiser le chan courant de la liste
        self.update_chan_list()

        # remmetre le focus sur la zone de texte
        self.Telegram_ui.main_columns.focus_position = 2
        self.Telegram_ui.right_side.focus_position = 1

# vim: ai ts=4 sw=4 et sts=4
