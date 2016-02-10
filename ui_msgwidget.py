#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import urwid

# Le widget utilise pour afficher la liste des messages
class MessageWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.msgs = []
        self.separator_pos = -1
        self.updateLocked = False
        self.Telegram_ui = Telegram_ui
        self.fix_getHist = []
        self.get_history()


    def get_history(self):
        while self.updateLocked:
            time.sleep(0.5)
        self.updateLocked = True
        self.separator_pos = -1

        self.prev_date = 1

        # Suppression des messages précédent (=redéfinition du widget)
        self.msg_list = urwid.SimpleFocusListWalker([urwid.Text(('top', " "), align='left')])
        super().__init__(self.msg_list)

        current_print_name = self.Telegram_ui.current_chan['print_name']

        # Hack pour fixer le problème des messages vide...
        if not current_print_name in self.fix_getHist:
            self.Telegram_ui.sender.history(current_print_name, 100)
            self.fix_getHist.append(current_print_name)

        msgDict = self.Telegram_ui.sender.history(current_print_name, 100)

        self.pos = 1
        for msg in msgDict:
            self.print_msg(msg)

        self.draw_separator()
        self.updateLocked = False



    def print_msg(self, msg):

        try:
            date = msg['date']
            try:
                text = msg['text']
            except:
                text = "media"

            try:
                sender = msg['from']['first_name']
            except:
                sender = msg['sender']['first_name']
        except:
            date = 1
            text = "empty message"
            sender = "Unknown"


        cur_date = time.strftime('│ %d/%m/%Y │', time.localtime(date))

        if cur_date != self.prev_date:
            date_text = '┌────────────┐\n' + cur_date + '\n└────────────┘'
            self.msg_list.insert(self.pos + 1, urwid.Text(('date', date_text), align='center'))
            self.focus_position = self.pos
            self.pos = self.pos +1
            self.prev_date = cur_date

        hour = time.strftime(' %H:%M ', time.localtime(date))
        color = self.get_name_color(sender)

        size_name = 9

        message_meta = urwid.Text([('hour', hour),
                                   (color, '{0: >9}'.format(sender[0:size_name])),
                                   ('dark gray', " │ ")])

        message_text = urwid.Text(text)
        self.msg_list.insert(self.pos +1,
                             urwid.Columns([(size_name +10, message_meta), message_text]))

        self.focus_position = self.pos
        self.pos = self.pos +1

    def draw_separator(self):
        if self.separator_pos != -1:
            self.delete_separator()
        self.separator_pos = self.pos
        self.pos = self.pos +1
        self.msg_list.insert(self.pos, urwid.AttrMap(urwid.Divider('-'), 'separator'))
        self.focus_position = self.pos -1

    def delete_separator(self):
        if self.separator_pos != -1:
            del self.msg_list[self.separator_pos]
            self.pos = self.pos -1
            self.separator_pos = -1


    def get_name_color(self, name):
        list_color = ['dark red',
                      'dark green',
                      'brown',
                      'dark blue',
                      'dark magenta',
                      'dark cyan',
                      'light gray',
                      'light red',
                      'light green',
                      'yellow',
                      'light blue',
                      'light magenta',
                      'light cyan',
                      'white']

        color = int(''.join(str(ord(c)) for c in name)) % len(list_color)
        return list_color[color]


# vim: ai ts=4 sw=4 et sts=4
