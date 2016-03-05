#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time

import urwid
import configparser

try:
    from pytg import Telegram
except:
    print("pytg needed, can be installed with:")
    print("$ pip install --user pytg==0.4.5")
    sys.exit(1)

    
from ui_chanwidget import ChanWidget
from ui_msgwidget import MessageWidget
from ui_msgsendwidget import MessageSendWidget
from msg_receiver import MessageReceiver


def gen_palette():
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
    ans = []
    for fg in table:
        ans.append((fg,fg,''))
        for bg in table:
            ans.append((fg+bg,fg,bg))

    for bg in table:
        ans.append(('b'+bg,'',bg))

    return ans



class Telegram_ui:
    def __init__(self, conf):

        self.lock_receiver = True
        self.conf = conf

        # Just shortcut for some configurations :
        self.DATE_FORMAT = self.conf['general']['date_format']
        self.NINJA_MODE = self.conf['general']['ninja_mode']
        self.INLINE_IMAGE = self.conf['general']['inline_image']

        self.start_Telegram()
        self.last_online = 1

        palette_init = [('status_bar', self.conf['style']['status_bar_fg'], self.conf['style']['status_bar_bg']),
                        ('date', self.conf['style']['date'], ''),
                        ('hour', self.conf['style']['hour'], ''),
                        ('separator', self.conf['style']['separator'], ''),
                        ('reversed', 'standout', ''),
                        ('cur_chan', self.conf['style']['cur_chan'], '')]
                   
        palette = palette_init + gen_palette()

        # Notification
        if self.conf['general']['notification']:
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

        self.main_loop = urwid.MainLoop((self.main_columns), palette, unhandled_input=self.unhandle_key, screen=urwid.raw_display.Screen())
        self.main_loop.screen.set_terminal_properties(colors=256)
        self.me = self.sender.get_self()
        self.lock_receiver = False
        self.main_loop.run()


    def display_notif(self, msg):
        if self.conf['general']['notification']:
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

    def is_image(self, path):
        return not path == None and (path.endswith('png') \
        or path.endswith('jpg') \
        or path.endswith('jpeg') \
        or path.endswith('JPG') \
        or path.endswith('PNG'))


    def download_media(self, msg):
        mtype = msg['media']['type']
        mid = msg['id']

        if mtype == 'photo':
            file = self.sender.load_photo(mid)['result']

        elif mtype == 'document':
            file = self.sender.load_document(mid)['result']
        else:
            file = None

        return file

    def open_file(self, path):
        if self.conf['general']['open_file'] and path != None:
            subprocess.Popen(['xdg-open', path], stderr=subprocess.DEVNULL)


    def start_Telegram(self):
        # Liaison avec telegram-cli
        PATH_TELEGRAM = self.conf['general']['path_telegram']
        PATH_PUBKEY = self.conf['general']['path_pubkey']

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
        if self.conf['general']['notification']:
            Notify.uninit()
        sys.stdout.write("\x1b]2;\x07")
        self.stop_Telegram()
        raise urwid.ExitMainLoop


    def unhandle_key(self, key):
        if key == self.conf['keymap']['quit']:
            self.exit()

        elif key == 'esc':
            self.msg_widget.draw_separator()

        elif key == self.conf['keymap']['prev_chan']:
            self.chan_widget.go_prev_chan()

        elif key == self.conf['keymap']['next_chan']:
            self.chan_widget.go_next_chan()

        elif key == self.conf['keymap']['open_file'] and \
                not self.last_media == {} and \
                self.conf['general']['open_file']:
            path = self.download_media(self.last_media)
            self.open_file(path)

        elif key == self.conf['keymap']['insert_text']:
            self.main_columns.focus_position = 2
            self.right_side.focus_position = 1



if __name__ == "__main__":
    
    conffile = os.path.dirname(os.path.abspath(__file__))+'/ncTelegram.conf'
    config = configparser.ConfigParser()
    config.read(conffile)

    config_full = {}

    config_full['general'] = {}
    config_full['style'] = {}
    config_full['keymap'] = {}

    config_full['general']['path_telegram'] = config['general'].get('path_telegram', "/usr/bin/telegram-cli")
    config_full['general']['path_pubkey'] = config['general'].get('path_pubkey', "/etc/telegram-cli/server.pub")
    config_full['general']['notification'] = config['general'].getboolean('notification', True)
    config_full['general']['ninja_mode'] = config['general'].getboolean('ninja_mode', False)
    config_full['general']['inline_image'] = config['general'].getboolean('inline_image', True)
    config_full['general']['open_file'] = config['general'].getboolean('open_file', True)
    config_full['general']['date_format'] = config['general'].get('date_format', "%x", raw=True)


    config_full['style']['status_bar_fg'] = config['style'].get('status_bar_fg', 'bold, white')
    config_full['style']['status_bar_bg'] = config['style'].get('status_bar_bg', 'dark gray')
    config_full['style']['date'] = config['style'].get('date', 'light green')
    config_full['style']['hour'] = config['style'].get('hour', 'dark gray')
    config_full['style']['separator'] = config['style'].get('separator', 'dark gray')
    config_full['style']['cur_chan'] = config['style'].get('cur_chan', 'light green')

    config_full['keymap']['left'] = config['keymap'].get('left', 'h')
    config_full['keymap']['right'] = config['keymap'].get('right', 'l')
    config_full['keymap']['up'] = config['keymap'].get('up', 'k')
    config_full['keymap']['down'] = config['keymap'].get('down', 'j')
    config_full['keymap']['quit'] = config['keymap'].get('quit', 'q')
    config_full['keymap']['insert_text'] = config['keymap'].get('insert_text', 'i')
    config_full['keymap']['open_file'] = config['keymap'].get('open_file', 'ctrl o')
    config_full['keymap']['next_chan'] = config['keymap'].get('next_chan', 'ctrl n')
    config_full['keymap']['prev_chan'] = config['keymap'].get('prev_chan', 'ctrl p')

    if not 'DISPLAY' in os.environ:
        config_full['general']['notification'] = False
        config_full['general']['open_file'] = False
    
    if config_full['general']['notification']:
        try:
            import gi
            gi.require_version('Notify', '0.7')
            from gi.repository import Notify
        except:
            config_full['general']['notification'] = False


    Telegram_ui(config_full)


# vim: ai ts=4 sw=4 et sts=4
