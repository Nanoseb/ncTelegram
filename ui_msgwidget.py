#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
import urwid



# Le widget utilise pour afficher la liste des messages
class MessageWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.msgs = []
        self.separator_pos = -1
        self.updateLocked = False
        self.Telegram_ui = Telegram_ui
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

        current_cmd = self.Telegram_ui.current_chan['cmd']
        self.pos = 1

        if current_cmd not in self.Telegram_ui.msg_buffer:

            current_print_name = self.Telegram_ui.current_chan['print_name']

            # Hack pour fixer le problème des messages vide...
            self.Telegram_ui.sender.history(current_print_name, 100)
            msgList = self.Telegram_ui.sender.history(current_print_name, 100)
            
            self.Telegram_ui.msg_buffer[current_cmd] = msgList


        for msg in self.Telegram_ui.msg_buffer[current_cmd]:
            self.print_msg(msg)

        self.draw_separator()

        self.updateLocked = False



    def print_msg(self, msg):

        date = msg['date']


        if 'text' in msg:
            text = msg['text']
        else:
            if 'action' in msg:
                text = '➜ ' + msg['action']['type'].replace('_',' ')

            if 'media' in msg:
                self.Telegram_ui.last_media = msg
                if msg['media']['type'] == 'photo':
                    if self.Telegram_ui.INLINE_IMAGE:
                        file = self.Telegram_ui.sender.load_photo(msg['id'])['result']
                        try:
                            raw_text = subprocess.check_output(['img2txt', file, '-f', 'utf8', '-H', '12'])
                            text = translate_color(raw_text)
                        except:
                            text = "➜ photo " + msg['media']['caption']
                    else:
                        text = "➜ photo " + msg['media']['caption']

                else:
                    text = "➜ " + msg['media']['type']
    

        if 'from' in msg:
            sender = msg['from']['first_name']
            sender_id = msg['from']['id']
        else:
            sender = msg['sender']['first_name']
            sender_id = msg['sender']['id']


            

        cur_date = time.strftime('│ ' + self.Telegram_ui.DATE_FORMAT + ' │', time.localtime(date))

        if cur_date != self.prev_date:
            fill = '─'*(len(cur_date) - 2)
            date_text = '┌' + fill + '┐\n' + cur_date + '\n└' + fill + '┘'
            self.msg_list.insert(self.pos + 1, urwid.Text(('date', date_text), align='center'))
            self.focus_position = self.pos
            self.pos = self.pos +1
            self.prev_date = cur_date

        hour = time.strftime(' %H:%M ', time.localtime(date))
        color = self.get_name_color(sender_id)

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
        current_cmd = self.Telegram_ui.current_chan['cmd']


        if not self.Telegram_ui.NINJA_MODE and (self.Telegram_ui.last_online - int(time.time())) > 5:
            # mark messages as read
            current_print_name = self.Telegram_ui.current_chan['print_name']
            self.Telegram_ui.sender.mark_read(current_print_name)
            self.Telegram_ui.sender.status_online()
            self.Telegram_ui.sender.status_offline()
            self.Telegram_ui.last_online = int(time.time())
    
        self.separator_pos = self.pos

        if current_cmd in self.Telegram_ui.chan_widget.msg_chan:
            self.separator_pos -= self.Telegram_ui.chan_widget.msg_chan[current_cmd]

        self.pos = self.pos +1
        self.msg_list.insert(self.separator_pos, urwid.AttrMap(urwid.Divider('-'), 'separator'))
        self.focus_position = self.separator_pos

    def delete_separator(self):
        if self.separator_pos != -1:
            del self.msg_list[self.separator_pos]
            self.pos = self.pos -1
            self.separator_pos = -1


    def get_name_color(self, id):
        list_color = ['dark red',
                'dark blue',
                'dark cyan',
                'dark green',
                'dark magenta',
                'brown',
                'light magenta',
                'light green',
                'yellow',
                'light blue',
                'light red',
                'light cyan',
                'light gray',
                ]

        color = id % len(list_color)
        return list_color[color]

    def keypress(self, size, key):
        key = super(MessageWidget, self).keypress(size, key)

        if key == 'j':
            self.keypress(size, 'down')
        elif key == 'k':
            self.keypress(size, 'up')
        elif key == 'h':
            self.Telegram_ui.main_columns.focus_position = 0
        else:
            return key


    def mouse_event(self, size, event, button, col, row, focus):

        if button == 4:
            self.keypress(size, 'up')
            self.keypress(size, 'up')

        if button == 5:
            self.keypress(size, 'down')
            self.keypress(size, 'down')










# Translate raw_text (ansi sequence) to something readable by urwid (attribut and text)
def translate_color(raw_text):

    table = ['black',
        'dark red',
        'dark green',
        'brown',
        'dark blue',
        'dark magenta',
        'dark cyan',
        'light gray',
        'dark gray',
        'light red',
        'light green',
        'yellow',
        'light blue',
        'light magenta',
        'light cyan',
        'white']
    formated_text = []
    raw_text = raw_text.decode("utf-8")

    for at in raw_text.split(u"\x1b["):
        nocolor = False
        try:
            attr, text = at.split("m",1)
        except:
            attr = '0'
            nocolor = True
            text = at.split("m",1)
        list_attr = [ int(i) for i in attr.split(';') ]
        list_attr.sort()
        fg = 0
        bg = 0
        
        if not nocolor:
            for elem in list_attr:
                if elem <= 37:
                    fg = elem - 30
                elif elem <= 47:
                    bg = elem - 40
                elif elem <= 94:
                    fg = fg + 8
                elif elem >= 100 and elem <= 104:
                    bg = bg + 8
                
                if fg < 0:
                    fg = 0
                if bg < 0:
                    bg = 0

                fgcolor = table[fg]
                bgcolor = table[bg]

                attribut = ''
                if fg == 0:
                    attribut = 'b'+bgcolor
                elif bg == 0:
                    attribut = fgcolor
                else:
                    attribut = fgcolor + bgcolor
        else:
            attribut = ''

        formated_text.append((attribut, text))



    return formated_text

# vim: ai ts=4 sw=4 et sts=4
