#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
import urwid
import re
import urllib.request



# widget used to print the message list
class MessageWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.urlregex = re.compile("""((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")
        self.msgs = []
        self.img_buffer = {}
        self.url_buffer = {}
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


        # deletion of previous messages
        self.msg_list = [] # urwid.SimpleFocusListWalker([urwid.Text(('top', " "), align='left')])
        super().__init__(self.msg_list)

        current_cmd = self.Telegram_ui.current_chan['id']
        self.pos = 0

        if current_cmd not in self.Telegram_ui.msg_buffer:

            current_print_name = self.Telegram_ui.current_chan['print_name']

            # hack to fix empty message bug (from telegram-cli probably)
            #self.Telegram_ui.sender.history(current_print_name, 100)

            msgList = self.Telegram_ui.sender.history(current_print_name, 100)
            
            self.Telegram_ui.msg_buffer[current_cmd] = msgList


        for msg in self.Telegram_ui.msg_buffer[current_cmd]:
            self.print_msg(msg)

        self.draw_separator()

        self.updateLocked = False


    def print_msg(self, msg):

        date = msg['date']


        if 'text' in msg:
            text = [msg['text']]
            urls = self.urlregex.findall(text[0])
            
            if urls:
                url = urls[0][0]
                if not url.startswith('http'):
                    url = 'http://' + url

                self.Telegram_ui.last_media = {'url': url}

                if url in self.url_buffer:
                    text = text + ['\n ➜ ' + self.url_buffer[url]]
                elif date > self.Telegram_ui.boot_time:
                    try:
                        resource = urllib.request.urlopen(url)
                        page = resource.read().decode(resource.headers.get_content_charset())
                        title = re.search('<title>(.*?)</title>', page, re.IGNORECASE|re.DOTALL).group(1)
                        self.url_buffer[url] = title
                        text = text + ['\n  ➜  ' + title]
                    except:
                        self.url_buffer[url] = ''
                 
                
        elif 'action' in msg:
            text = [(urwid.AttrSpec('light gray', ''), '➜ ' + msg['action']['type'].replace('_',' '))]


        elif 'media' in msg:
            self.Telegram_ui.last_media = msg
            text = [(urwid.AttrSpec('light gray', ''), "➜ " + msg['media']['type'])]
            if 'caption' in msg['media']:
                text = text + [" " + msg['media']['caption']]

            if self.Telegram_ui.INLINE_IMAGE:
                image = self.get_inline_img(msg)
                if image != None:
                    text = text + ['\n'] + self.get_inline_img(msg)


        if 'from' in msg:
            sender = msg['from']['first_name']
            sender_id = msg['from']['peer_id']
        else:
            sender = msg['sender']['first_name']
            sender_id = msg['sender']['peer_id']
            

        color = self.get_name_color(sender_id)

        if 'reply_id' in msg:
            msg_reply = self.Telegram_ui.sender.message_get(msg['reply_id'])

            if 'from' in msg_reply:
                sender_reply = msg_reply['from']['first_name']
                sender_reply_id = msg_reply['from']['peer_id']
            else:
                sender_reply = msg_reply['sender']['first_name']
                sender_reply_id = msg_reply['sender']['peer_id']

            color_reply = self.get_name_color(sender_reply_id)
            if 'text' in msg_reply:
                plus = ''
                if len(msg_reply['text']) > 40:
                    plus = '...'
                text = [(urwid.AttrSpec('light gray', ''), 'reply to ➜  '),
                        (urwid.AttrSpec(color_reply, '') , sender_reply),
                        ': ' + msg_reply['text'][:40] + plus + '\n'] + text
            else:
                text = [(urwid.AttrSpec('light gray', ''), 'reply to ➜  '),
                        (urwid.AttrSpec(color_reply, '') , sender_reply),
                        '\n'] + text


        if 'fwd_from' in msg:
            color_fwd = self.get_name_color(msg['fwd_from']['peer_id'])
            text = [(urwid.AttrSpec('light gray', ''), 'forwarded from '),
                    (urwid.AttrSpec(color_fwd, ''), msg['fwd_from']['first_name'] + '\n')] + text

            

        cur_date = time.strftime('│ ' + self.Telegram_ui.DATE_FORMAT + ' │', time.localtime(date))

        if cur_date != self.prev_date:
            fill = '─'*(len(cur_date) - 2)
            date_text = '┌' + fill + '┐\n' + cur_date + '\n└' + fill + '┘'
            self.msg_list.insert(self.pos + 1, urwid.Text(('date', date_text), align='center'))
            self.focus_position = self.pos
            self.pos = self.pos +1
            self.prev_date = cur_date

        hour = time.strftime(' %H:%M ', time.localtime(date))

        size_name = 9

        message_meta = urwid.Text([('hour', hour),
                                   (urwid.AttrSpec(color, 'default'), '{0: >9}'.format(sender[0:size_name])),
                                   ('separator', " │ ")])

        message_text = urwid.Text(text)
        self.msg_list.insert(self.pos +1,
                             urwid.Columns([(size_name +10, message_meta), message_text]))

        self.focus_position = self.pos
        self.pos = self.pos +1


    def draw_separator(self):
        if self.separator_pos != -1:
            self.delete_separator()
        current_cmd = self.Telegram_ui.current_chan['id']

        if not self.Telegram_ui.NINJA_MODE and current_cmd in self.Telegram_ui.chan_widget.msg_chan: 
            # mark messages as read
            current_print_name = self.Telegram_ui.current_chan['print_name']
            self.Telegram_ui.sender.mark_read(current_print_name)
            self.Telegram_ui.sender.status_online()
            self.Telegram_ui.sender.status_offline()


        self.separator_pos = self.pos

        if current_cmd in self.Telegram_ui.chan_widget.msg_chan:
            self.separator_pos -= self.Telegram_ui.chan_widget.msg_chan[current_cmd]
            if self.separator_pos <= 0:
                self.separator_pos = 1
            del self.Telegram_ui.chan_widget.msg_chan[current_cmd]
            self.Telegram_ui.chan_widget.update_chan_list()
            self.Telegram_ui.print_title()

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


    def get_inline_img(self, msg):
        cmd = self.Telegram_ui.current_chan['id']
        mid = msg['id']
        key = cmd + str(mid)
        if key in self.img_buffer:
            return self.img_buffer[key]
        else:
            path = self.Telegram_ui.download_media(msg)

            if self.Telegram_ui.is_image(path):
                try:
                    raw_text = subprocess.check_output(['img2txt', path, '-f', 'utf8', '-H', '12'])
                    text = translate_color(raw_text)
                    self.img_buffer[key] = text
                    return text
                except:
                    return None 


    def keypress(self, size, key):
        key = super(MessageWidget, self).keypress(size, key)

        if key == self.Telegram_ui.conf['keymap']['down']:
            self.keypress(size, 'down')
        elif key == self.Telegram_ui.conf['keymap']['up']:
            self.keypress(size, 'up')
        elif key ==  self.Telegram_ui.conf['keymap']['left']:
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

    for at in raw_text.split("\x1b["):
        try:
            attr, text = at.split("m",1)
        except:
            attr = '0'
            text = at.split("m",1)

        list_attr = [ int(i) for i in attr.split(';') ]
        list_attr.sort()
        fg = -1
        bg = -1
       
        for elem in list_attr:
            if elem <= 29:
                pass
            elif elem <= 37:
                fg = elem - 30
            elif elem <= 47:
                bg = elem - 40
            elif elem <= 94:
                fg = fg + 8
            elif elem >= 100 and elem <= 104:
                bg = bg + 8
            
        fgcolor = table[fg]
        bgcolor = table[bg]

        if fg < 0:
            fgcolor = ''
        if bg < 0:
            bgcolor = ''

        if list_attr == [0]:
            fgcolor = ''
            bgcolor = ''

        formated_text.append((urwid.AttrSpec(fgcolor, bgcolor), text))

    return formated_text

# vim: ai ts=4 sw=4 et sts=4
