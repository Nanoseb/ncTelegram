#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import logging

import urwid

# TODO something cleaner to he here?
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

logger = logging.getLogger(__name__)

class Telegram_ui:
    def __init__(self, conf):
        # Boolean to prevent TgClient's to process updates
        self.lock_receiver = True

        # ncTelegram configuration as a dict
        self.conf = conf

        # Timestamp of start. Should be const
        self.boot_time = int(time.time())

        # Just shortcut for some configurations :
        self.DATE_FORMAT = self.conf['general']['date_format']
        self.NINJA_MODE = self.conf['general']['ninja_mode']
        self.INLINE_IMAGE = self.conf['general']['inline_image']

        # Actual telegram client, interacting with telegram's servers
        self.tg_client = TgClient(self)
        self.tg_client.start()

        # Dict per channel ([cmd]) telling if the user is online and since when is he offline
        self.online_status = {}
        # Dict per channel ([cmd]) telling if the user has read the last message sent
        self.read_status = {}

        style = self.conf['style']
        palette = [('status_bar', style['status_bar_fg'], style['status_bar_bg']),
                   ('date', style['date'], ''),
                   ('hour', style['hour'], ''),
                   ('separator', style['separator'], ''),
                   ('reversed', 'standout', ''),
                   ('cur_chan', style['cur_chan'], ''),
                   ('user_color', style['user_color'], '')
                   ]

        # Setup notifications if enabled
        if self.conf['general']['notification']:
            Notify.init("ncTelegram")
            self.image = '/usr/share/ncTelegram/t_logo.png'

        # cmd of the channel being currently displayed (the one selected)
        self.current_chan = {}

        # Dict per channel ([cmd]) containing the path to the last media (file, photo etc.) being sent to that channel
        # it is used with a shortcut to open the file using xdg-open (probably need to change, this is not a nice way of doing this)
        self.last_media = {}

        # message buffer init
        # msg_buffer is where incoming messages go before they have been printed
        self.msg_buffer = {}

        # msg_archive is where messages go once they are processed
        # and have the proper layout (urwid list)
        self.msg_archive = {}

        # Shortcut to retrieve the client's entity faster
        # TODO: might miss an update in profile ?
        self.me = self.tg_client.client.get_me()


        ## Create and setup UI
        # List of dialogs on the left
        self.chan_widget = ChanWidget(self)
        self.print_title() # TODO: remove implicit dependency on chan_widget
        # List of messages on the upper right
        self.msg_widget = MessageWidget(self)
        # Text area to write a message + status bar widget
        self.msg_send_widget = MessageSendWidget(self)

        # Right panel (list of messages + text area)
        self.right_side = urwid.Pile([self.msg_widget, (2, self.msg_send_widget)])
        vert_separator = urwid.AttrMap(urwid.Filler(urwid.Columns([])), 'status_bar')

        # Final arrangements
        self.main_columns = urwid.Columns([('weight', 1, self.chan_widget),
                                           (1, vert_separator),
                                           ('weight', 5, self.right_side)])

        # urwid's main loop, responsible for drawing on the screen
        self.main_loop = urwid.MainLoop(self.main_columns, palette,
                unhandled_input=self.unhandle_key)
        self.main_loop.screen.set_terminal_properties(colors=256)

        # Allow tgclient to process updates, and to call the UI as it's now ready
        self.lock_receiver = False

        # TODO: use start() + a with: block
        self.main_loop.run()

    def update_online_status(self, when, status, cmd):
        self.online_status[cmd] = (when, status)
        if cmd == self.current_chan.id:
            self.msg_send_widget.update_status_bar()

    def update_read_status(self, cmd, bool):
        self.read_status[cmd] = bool
        if cmd == self.current_chan.id:
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
                    self.msg_buffer[cmd] = self.tg_client.history(print_name, 100)
                except Exception as e:
                    logger.warning("Got exception %s while filling msg buffer", e)
                    self.msg_buffer[cmd] = []
                if self.INLINE_IMAGE:
                    for msg in self.msg_buffer[cmd]:
                        if 'media' in msg:
                            image = self.msg_widget.get_inline_img(msg)

        self.chan_widget.update_chan_list()

    def is_image(self, path):
        # TODO is that needed? consider file as file if not send as photo is probably better
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
        # TODO Not sure that's a good idea in the end, reconsider that, download file somewhere instead of opening it
        if self.conf['general']['open_file'] and path != None:
            subprocess.Popen(['xdg-open', path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)




    def stop_Telegram(self):
        self.tg_client.client.disconnect()


    def exit(self):
        if self.conf['general']['notification']:
            Notify.uninit()
        # TODO: remove the comment (but it erases error messages)
        #sys.stdout.write("\x1b]2;\x07")
        self.stop_Telegram()
        raise urwid.ExitMainLoop


    def unhandle_key(self, key):
        """
        Function called whenever urwid did not handle a key
        """
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
