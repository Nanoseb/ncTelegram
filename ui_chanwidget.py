#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urwid
import time

class NewButton(urwid.Button):
    def __init__(self, caption, callback,arg=None):
        super(NewButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback, arg)
        self._w = urwid.AttrMap(urwid.SelectableIcon(caption, 1),
                                None, focus_map='status_bar')

# Le widget utilise pour afficher la liste des chans
class ChanWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.chans = []
        self.updateLocked = False
        self.current_chan_pos = 0
        self.Telegram_ui = Telegram_ui
        self.msg_chan = {}        #nombre de message non lut par chan
        self.get_new_chan_list()

    def get_new_chan_list(self):
        if self.updateLocked:
            return

        self.updateLocked = True
        bool = True
        while bool:
            try:
                # list contenant les chans
                self.chans = self.Telegram_ui.sender.dialog_list()
                bool = False
            except:
                time.sleep(0.3)
                pass

        # On ajoute cmd en champ de la liste de chan
        for i in range(len(self.chans)):
            chan = self.chans[i]
            self.chans[i]['cmd'] = chan['type'] + "#" + str(chan['id'])


        self.updateLocked = False
        self.update_chan_list()


    # Mettre a jour la liste des chans
    def update_chan_list(self):

        # Réécriture de la liste, pour actualiser le chan courant
        self.chan_list = urwid.SimpleFocusListWalker([urwid.AttrMap(urwid.Text("Chan list:"), 'status_bar')])
        super().__init__(self.chan_list)


        if self.Telegram_ui.current_chan == []:
            self.Telegram_ui.current_chan = self.chans[-1]

        pos = self.focus_position
        
        i = len(self.chans) -1
        # Construction de la liste de chan
        for chan in self.chans[::-1]:
            print_name = chan['print_name']

            cmd = chan['cmd']

            label = print_name.replace('_', ' ')

            if chan['type'] == 'user':
                label = "➜  " + label
            else:
                label = "➜➜ " + label

            if cmd in self.msg_chan:
                label = label + ' [' + str(self.msg_chan[cmd]) + ']'

            if print_name == self.Telegram_ui.current_chan['print_name']:
                button = NewButton(('cur_chan', label), self.chan_change, chan)
                current_pos = pos + 1
                self.current_chan_pos = i
            else:
                button = NewButton(label, self.chan_change, chan)

            self.chan_list.insert(pos +1, button)
            pos = pos + 1
            i -= 1

        self.chan_list.insert(pos +1, urwid.AttrMap(urwid.Divider('─'), 'separator'))
        pos = pos + 1
        self.chan_list.insert(pos +1, urwid.Text('✚  Create new group chat'))
        pos = pos + 1
        self.chan_list.insert(pos +1, urwid.Text('✚  Create new channel'))
        pos = pos + 1
        self.chan_list.insert(pos +1, urwid.Text('☺  Contacts'))
        pos = pos + 1
        self.chan_list.insert(pos +1, urwid.AttrMap(urwid.Divider('─'), 'separator'))

        
        # on affiche le bouton uniquement s'il est utile
        list_buff = [ cmd for cmd in self.Telegram_ui.msg_buffer.keys() ]
        list_chan = [ chan['cmd'] for chan in self.chans ]

        list_buff.sort()
        list_chan.sort()
        if list_buff != list_chan :
            pos = pos + 1
            button = NewButton('⬇  Download message buffer', self.Telegram_ui.fill_msg_buffer)
            self.chan_list.insert(pos +1, button)


        self.focus_position = current_pos

    def add_msg(self, cmd):
        """ incrémentation des messages non lut
        """
        if cmd in self.msg_chan:
            self.msg_chan[cmd] = self.msg_chan[cmd] + 1
        else:
            self.msg_chan[cmd] = 1

        self.Telegram_ui.print_title()


    def go_next_chan(self):
        self.current_chan_pos -= 1
        if self.current_chan_pos < 0:
            nb_chan = len(self.chans) 
            self.current_chan_pos = nb_chan -1
        self.chan_change('bu', self.chans[self.current_chan_pos])


    def go_prev_chan(self):
        nb_chan = len(self.chans) 
        self.current_chan_pos += 1
        if self.current_chan_pos > nb_chan -1:
            self.current_chan_pos = 0
        self.chan_change('bu', self.chans[self.current_chan_pos])


    def chan_change(self, button, chan):

        self.Telegram_ui.current_chan = chan

        current_cmd = chan['cmd'] 

        self.Telegram_ui.last_media = {}
        self.Telegram_ui.msg_send_widget.update_send_widget()
        self.Telegram_ui.msg_widget.get_history()

        # suppression des messages non lut pour le nouveau chan
        if current_cmd in self.msg_chan:
            del self.msg_chan[current_cmd]
            self.Telegram_ui.print_title()
        #Appel pour actualiser le chan courant de la liste
        self.update_chan_list()

        # remmetre le focus sur la zone de texte
        self.Telegram_ui.main_columns.focus_position = 2
        self.Telegram_ui.right_side.focus_position = 1


    def keypress(self, size, key):
        key = super(ChanWidget, self).keypress(size, key)

        if key == 'j':
            self.keypress(size, 'down')
        elif key == 'k':
            self.keypress(size, 'up')
        elif key == 'l':
            self.Telegram_ui.main_columns.focus_position = 2
        else:
            return key



# vim: ai ts=4 sw=4 et sts=4
