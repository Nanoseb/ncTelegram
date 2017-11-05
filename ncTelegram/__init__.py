#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time

import urwid

try:
    import gi
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify
except:
    pass

from .ui_chanwidget import ChanWidget
from .ui_msgwidget import MessageWidget
from .ui_msgsendwidget import MessageSendWidget
from .tg_client import TgClient



class Telegram_ui:
    def __init__(self, conf):
        self.lock_receiver = True
        self.conf = conf

        self.boot_time = int(time.time())
        # Just shortcut for some configurations :
        self.DATE_FORMAT = self.conf['general']['date_format']
        self.NINJA_MODE = self.conf['general']['ninja_mode']
        self.INLINE_IMAGE = self.conf['general']['inline_image']

        print("Gonna build msg_receiver")
        self.tg_client = TgClient(self)

        self.last_online = 1
        self.online_status = {}
        self.read_status = {}

        palette = [('status_bar', self.conf['style']['status_bar_fg'], self.conf['style']['status_bar_bg']),
                   ('date', self.conf['style']['date'], ''),
                   ('hour', self.conf['style']['hour'], ''),
                   ('separator', self.conf['style']['separator'], ''),
                   ('reversed', 'standout', ''),
                   ('cur_chan', self.conf['style']['cur_chan'], ''),
                   ('user_color', self.conf['style']['user_color'], '')
                   ]

        # Notification
        if self.conf['general']['notification']:
            Notify.init("ncTelegram")
            self.image = '/usr/share/ncTelegram/t_logo.png'

        self.current_chan = {}
        self.last_media = {}

        # message buffer init
        # msg_buffer is where incoming messages go before they have been printed
        self.msg_buffer = {}
        # msg_archive is where messages go once they are processed and have the proper layout (urwid list)
        self.msg_archive = {}

        self.chan_widget = ChanWidget(self)
        print("Chan widget ok!")

        self.print_title()
        self.me = self.tg_client.get_me()

        self.msg_widget = MessageWidget(self)

        # message writing + status bar widget
        self.msg_send_widget = MessageSendWidget(self)

        # Right pannel
        self.right_side = urwid.Pile([self.msg_widget, (2, self.msg_send_widget)])

        vert_separator = urwid.AttrMap(urwid.Filler(urwid.Columns([])), 'status_bar')

        # Final arrangements
        self.main_columns = urwid.Columns([('weight', 1, self.chan_widget),
                                           (1, vert_separator),
                                           ('weight', 5, self.right_side)])

        self.main_loop = urwid.MainLoop((self.main_columns), palette,
                unhandled_input=self.unhandle_key, screen=urwid.raw_display.Screen())
        self.main_loop.screen.set_terminal_properties(colors=256)
        self.lock_receiver = False
        self.main_loop.run()

    def update_online_status(self, when, status, cmd):
        self.online_status[cmd] = (when, status)
        if cmd == self.current_chan['id']:
            self.msg_send_widget.update_status_bar()

    def update_read_status(self, cmd, bool):
        self.read_status[cmd] = bool
        if cmd == self.current_chan['id']:
            self.msg_send_widget.update_status_bar()


    def display_notif(self, msg):
        if self.conf['general']['notification']:
            text = msg['text']

            if msg['receiver']['type'] == 'user':
                sender = msg['sender']['first_name']
            else:
                sender = msg['receiver']['name'] + ": " + msg['sender']['first_name']


            Notify.Notification.new('', '<b>' + sender + '</b>\n' + text, self.image).show()


    def print_title(self):
        total_msg_waiting = sum(self.chan_widget.msg_chan.values())
        if total_msg_waiting == 0:
            sys.stdout.write("\x1b]2;ncTelegram\x07")
        else:
            sys.stdout.write("\x1b]2;ncTelegram (" + str(total_msg_waiting) + ")\x07")


    def fill_msg_buffer(self, button):

        for chan in self.chan_widget.chans:
            cmd = chan['id']
            if cmd not in self.msg_buffer:
                print_name = chan['print_name']
                try:
                    self.msg_buffer[cmd] = self.sender.history(print_name, 100)
                except:
                    self.msg_buffer[cmd] = []
                if self.INLINE_IMAGE:
                    for msg in self.msg_buffer[cmd]:
                        if 'media' in msg:
                            image = self.msg_widget.get_inline_img(msg)

        self.chan_widget.update_chan_list()

    def is_image(self, path):
        return not path == None and (path.endswith('png') \
        or path.endswith('jpg') \
        or path.endswith('jpeg') \
        or path.endswith('JPG') \
        or path.endswith('PNG'))


    def download_media(self, msg):
        if 'url' in msg:
            return msg['url']
        else:
            mtype = msg['media']['type']
            mid = msg['id']

            #file = self.sender.load_file(mid)
            if mtype == 'photo':
                file = self.sender.load_photo(mid)

            elif mtype == 'document':
                file = self.sender.load_document(mid)
            else:
                file = None

            return file

    def open_file(self, path):
        if self.conf['general']['open_file'] and path != None:
            subprocess.Popen(['xdg-open', path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)




    def stop_Telegram(self):
        self.tg.disconnect()


    def exit(self):
        if self.conf['general']['notification']:
            Notify.uninit()
        sys.stdout.write("\x1b]2;\x07")
        self.stop_Telegram()
        raise urwid.ExitMainLoop


    def unhandle_key(self, key):
        if key == self.conf['keymap']['quit']:
            self.exit()

        elif key == self.conf['keymap']['hide_chanlist']:

            if 1 == self.main_columns.contents[0][1][1]:    # check if already hidden
                # hidding
                self.main_columns.contents[0] = (self.main_columns.contents[0][0],('given', 0, False) )
                self.main_columns.contents[1] = (self.main_columns.contents[1][0],('given', 0, False) )
            else:
                self.main_columns.contents[0] = (self.main_columns.contents[0][0],('weight', 1, True) )
                self.main_columns.contents[1] = (self.main_columns.contents[1][0],('given', 1, False) )


        elif key == 'esc':
            self.msg_widget.draw_separator()

        elif key == self.conf['keymap']['prev_chan']:
            self.chan_widget.go_prev_chan()

        elif key == self.conf['keymap']['next_chan']:
            self.chan_widget.go_next_chan()

        elif key == self.conf['keymap']['open_file'] and \
                self.last_media[self.current_chan['id']] != {} and \
                        self.conf['general']['open_file']:
             path = self.download_media(self.last_media[self.current_chan['id']])
             self.open_file(path)

        elif key == self.conf['keymap']['insert_text']:
            self.main_columns.focus_position = 2
            self.right_side.focus_position = 1

        elif key == "'":
            self.main_columns.focus_position = 2
            self.right_side.focus_position = 1
            self.msg_send_widget.widgetEdit.insert_text("'")

# vim: ai ts=4 sw=4 et sts=4
