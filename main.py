#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time

import urwid

try:
    from pytg import Telegram
except:
    print("pytg needed, can be installed with:")
    print("pip install --user pytg")
    sys.exit(1)

if not 'DISPLAY' in os.environ:
    NOTIF = False
    VIEW_IMAGES = False
else:
    try:
        import gi
        gi.require_version('Notify', '0.7')
        from gi.repository import Notify
        NOTIF = True
    except:
        NOTIF = False
    
    try:
        from PIL import Image
        VIEW_IMAGES = True
    except:
        VIEW_IMAGES = False


from ui_infobar import InfoBar
from ui_chanwidget import ChanWidget
from ui_msgwidget import MessageWidget
from ui_msgsendwidget import MessageSendWidget
from msg_receiver import MessageReceiver


PATH_TELEGRAM = "/usr/bin/telegram-cli"
PATH_PUBKEY = "/etc/telegram-cli/server.pub"
NOTIF_LEVEL = "all" # or "hl"
NINJA_MODE = False
#DATE_FORMAT = "%d/%m/%Y"
#DATE_FORMAT = "%A %d %B"
DATE_FORMAT = "%x"

class Telegram_ui:
    def __init__(self):

        global NOTIF, PATH_TELEGRAM, PATH_PUBKEY, NOTIF_LEVEL, VIEW_IMAGES, DATE_FORMAT, NINJA_MODE
        self.lock_receiver = True
        self.DATE_FORMAT = DATE_FORMAT
        self.NINJA_MODE = NINJA_MODE
        self.start_Telegram()

        palette = [('status_bar', 'bold,white', 'dark gray'),
                   ('date', 'light green', ''),
                   ('hour', 'dark gray', ''),
                   ('separator', 'dark gray', ''),
                   ('reversed', 'standout', ''),
                   ('cur_chan', 'light green', ''),
                   ('dark red', 'dark red', ''),
                   ('dark green', 'dark green', ''),
                   ('brown', 'brown', ''),
                   ('dark blue', 'dark blue', ''),
                   ('dark magenta', 'dark magenta', ''),
                   ('dark cyan', 'dark cyan', ''),
                   ('light gray', 'light gray', ''),
                   ('dark gray', 'dark gray', ''),
                   ('light red', 'light red', ''),
                   ('light green', 'light green', ''),
                   ('light blue', 'light blue', ''),
                   ('light magenta', 'light magenta', ''),
                   ('light cyan', 'light cyan', ''),
                   ('white', 'white', ''),]

        # Notification
        if NOTIF:
            Notify.init("ncTelegram")
            self.image = os.path.dirname(os.path.abspath(__file__))+'/t_logo.png'

        self.current_chan = []
        self.last_media = {}

        # Cache des messages
        self.msg_buffer = {}

        # Liste des chans
        self.chan_widget = ChanWidget(self)

        # barre de titre
        self.print_title()

        # Liste des messages
        self.msg_widget = MessageWidget(self)

        # Envoie de messages
        self.msg_send_widget = MessageSendWidget(self)

        # Thread du dump de messages
        self.msg_dump = MessageReceiver(self)
        self.msg_dump.daemon = True
        self.msg_dump.start()

        # Panneau droit
        self.right_side = urwid.Pile([self.msg_widget, (2, self.msg_send_widget)])

        vert_separator = urwid.AttrMap(urwid.Filler(urwid.Columns([])), 'status_bar')

        # Arrangements finaux
        self.main_columns = urwid.Columns([('weight', 1, self.chan_widget),
                                           (1, vert_separator),
                                           ('weight', 5, self.right_side)])
        #main_pile = urwid.Pile([(1, title_bar), self.main_columns,])

        self.main_loop = urwid.MainLoop((self.main_columns), palette, unhandled_input=self.unhandle_key)
        self.main_loop.screen.set_terminal_properties(colors=16)
        self.me = self.sender.get_self()
        self.lock_receiver = False
        self.main_loop.run()


    def display_notif(self, msg):
        if NOTIF:
            text = msg['text']

            try:
                sender = msg['peer']['first_name']
            except:
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
    
            cmd = chan['cmd']
            if cmd not in self.msg_buffer:
                print_name = chan['print_name']
                self.sender.history(print_name, 100)
                self.msg_buffer[cmd] = self.sender.history(print_name, 100)

        self.chan_widget.update_chan_list()


    def load_last_media(self):
        if self.last_media == {} or not VIEW_IMAGES:
            return
    
        media = {}
        mtype = self.last_media['media']['type']
        mid =  self.last_media['id']

        if mtype == 'photo':
            media = self.sender.load_photo(mid)

        elif mtype == 'document':
            media = self.sender.load_document(mid)

        elif mtype == 'file':
            media = self.sender.load_file(mid)

        if not media == {} and (media['result'].endswith('png') \
                or media['result'].endswith('jpg') \
                or media['result'].endswith('jpeg') \
                or media['result'].endswith('JPG') \
                or media['result'].endswith('PNG')): 

            Image.open(media['result']).show()



    def start_Telegram(self):
        # Liaison avec telegram-cli
        self.tg = Telegram(telegram=PATH_TELEGRAM,
                           pubkey_file=PATH_PUBKEY)
        self.receiver = self.tg.receiver
        self.sender = self.tg.sender
        self.receiver.start()


    def stop_Telegram(self):
        #self.tg.stopCLI()
        self.sender.status_offline()
        self.sender.terminate()
        self.receiver.stop()


    def exit(self):
        if NOTIF:
            Notify.uninit()
        sys.stdout.write("\x1b]2;\x07")
        self.stop_Telegram()
        raise urwid.ExitMainLoop


    def unhandle_key(self, key):
        if key in('q', 'Q'):
            self.exit()

        elif key == 'esc':
            self.msg_widget.draw_separator()

        elif key == 'ctrl p':
            self.chan_widget.go_prev_chan()

        elif key == 'ctrl n':
            self.chan_widget.go_next_chan()

        elif key == 'ctrl o':
            self.load_last_media()

        elif key == 'i':
            self.main_columns.focus_position = 2
            self.right_side.focus_position = 1



if __name__ == "__main__":
    Telegram_ui()


# vim: ai ts=4 sw=4 et sts=4
