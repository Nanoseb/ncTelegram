#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urwid
import time

# Le widget utilise pour afficher la liste des chans
class ChanWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.chans = []
        self.updateLocked = False
        self.Telegram_ui = Telegram_ui
        self.msg_chan = {}        
        self.updateChanList()
   
    # Mettre a jour la liste des chans
    def updateChanList(self):
        while (self.updateLocked):
            time.sleep(0.1)
        self.updateLocked = True

        # Réécriture de la liste, pour actualiser le chan courant
        self.chan_list = urwid.SimpleFocusListWalker([urwid.Text("Chan"), urwid.Divider()])
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

        for i in self.chans[::-1]:
            print_name = i['print_name']
            
            cmd = i['type'] + "#" + str(i['id']) 

            if cmd in self.msg_chan:
                label = print_name.replace('_', ' ') + ' [' + str(self.msg_chan[cmd]) + ']' 
            else:
                label = print_name.replace('_', ' ')

            if print_name == self.Telegram_ui.current_chan['print_name'] :            
                button = urwid.Button(('cur_chan', label))
                current_pos = pos + 1
            else:
                button = urwid.Button(label)
    
            urwid.connect_signal(button, 'click', self.chan_change, print_name)
            self.chan_list.insert(pos +1, urwid.AttrMap(button, None, focus_map='reversed'))
            pos = pos + 1

        self.focus_position = current_pos
        self.updateLocked = False



    def add_msg(self, msg):
        cmd = msg['receiver']['cmd']  
   
        current_cmd = self.Telegram_ui.current_chan['type'] + "#" + str(self.Telegram_ui.current_chan['id']) 
        if cmd != current_cmd:
            if cmd in self.msg_chan:
                self.msg_chan[cmd] = self.msg_chan[cmd] + 1
            else:
                self.msg_chan[cmd] = 1

            self.Telegram_ui.total_msg_waiting = self.Telegram_ui.total_msg_waiting + 1
            self.Telegram_ui.print_title()

        self.updateChanList()
        


    def chan_change(self, button, print_name): 
        
        for i in self.chans:
            if i['print_name'] == print_name:
                self.Telegram_ui.current_chan = i
        
        current_cmd = self.Telegram_ui.current_chan['type'] + "#" + str(self.Telegram_ui.current_chan['id']) 
        
        if current_cmd in self.msg_chan:
            self.Telegram_ui.total_msg_waiting = self.Telegram_ui.total_msg_waiting - self.msg_chan[current_cmd]
            self.Telegram_ui.print_title()
            del self.msg_chan[current_cmd]

        self.Telegram_ui.msg_send_widget.update_send_widget()
        self.Telegram_ui.msg_widget.getHistory()

        #Appel pour actualiser le chan courant de la liste
        self.updateChanList()
        
        # remmetre le focus sur la zone de texte
        self.Telegram_ui.main_columns.focus_position = 2
        self.Telegram_ui.right_side.focus_position = 1

# vim: ai ts=4 sw=4 et sts=4
