#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urwid
import time
import logging
import telethon.tl.types as ttt

from .tg_client import get_print_name

class NewButton(urwid.Button):
    def __init__(self, caption, callback,arg=None):
        super(NewButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback, arg)
        self._w = urwid.AttrMap(urwid.SelectableIcon(caption, 1),
                                None, focus_map='status_bar')

class ChanWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.chans = {}
        self.updateLocked = False
        self.current_chan_pos = 0
        self.Telegram_ui = Telegram_ui
        self.msg_chan = {}        #unread count by chan
        self.get_new_chan_list()

    def get_new_chan_list(self):
        """
        Fetches the dialogs list.
        Locks the updates while doing so, if it cans.
        """
        if self.updateLocked:
            return

        self.updateLocked = True
        bool = True
        while bool:
            try:
                # list of pairs (dialog, entity)
                # TODO: find a better limit, or download dialogs with a limit
                self.chans = self.Telegram_ui.tg_client.dialog_list(limit=10)
                bool = False
            except Exception as e:
                logging.getLogger().warning("Couldn't download chans list", exc_info=True)
                time.sleep(0.5)

        # Setting up the users online time
        for dialog in self.chans:
            entity = dialog.entity
            if isinstance(entity, ttt.PeerUser):# and dialog.peer.user_id == user.id:
                id = entity.id
                if isinstance(entity.status, ttt.UserStatusOnline):
                    # TODO : put something else as an online time
                    self.Telegram_ui.online_status[id] = (str(entity.status.expires), False)
                elif isinstance(entity.status, ttt.UserStatusOffline):
                    self.Telegram_ui.online_status[id] = (str(entity.status.was_online), False)
                else:
                    self.Telegram_ui.online_status[id] = ('?', False)

        self.update_chan_list()
        self.updateLocked = False


    def update_chan_list(self):
        """
        Updates the urwid dialog list
        """

        # refresh of chan list
        self.chan_list = urwid.SimpleFocusListWalker([urwid.AttrMap(urwid.Text("Chan list:"), 'status_bar')])
        super().__init__(self.chan_list)


        if not self.Telegram_ui.current_chan:
            self.Telegram_ui.current_chan = self.chans[-1]

        pos = self.focus_position

        i = len(self.chans) -1

        # build of chan list
        for dialog in self.chans:
            entity = dialog.entity
            pos +=1

            print_name = get_print_name(entity)

            cmd = entity.id

            label = print_name.replace('_', ' ')

            if isinstance(entity, ttt.PeerUser):
                label = "➜  " + label
            elif isinstance(entity, ttt.PeerChat):
                label = "➜➜ " + label
            elif isinstance(entity, ttt.PeerChannel):
                label = "⤨  " + label

            if cmd in self.msg_chan and self.msg_chan[cmd] != 0:
                label = label + ' [' + str(self.msg_chan[cmd]) + ']'

            if print_name == self.Telegram_ui.current_chan.name:
                button = NewButton(('cur_chan', label), self.chan_change, (dialog, entity))
                current_pos = pos
                self.current_chan_pos = i
            else:
                button = NewButton(label, self.chan_change, (dialog, entity))

            self.chan_list.insert(pos, button)
            i -= 1

        if not 'current_pos' in locals():
            self.current_chan_pos = 1
            current_pos = pos -1


        pos +=1
        self.chan_list.insert(pos, urwid.AttrMap(urwid.Divider('─'), 'separator'))
        #pos += 1
        #self.chan_list.insert(pos, urwid.Text('✚  Create new group chat'))
        #pos += 1
        #self.chan_list.insert(pos, urwid.Text('✚  Create new channel'))
        #pos += 1
        #self.chan_list.insert(pos, urwid.Text('☺  Contacts'))
        #pos += 1
        #self.chan_list.insert(pos, urwid.AttrMap(urwid.Divider('─'), 'separator'))

        # print of buffer button only if needed
        list_buff = [ cmd for cmd in self.Telegram_ui.msg_buffer.keys() ]
        list_chan = [ chan.id for chan in self.chans ]

        list_buff.sort()
        list_chan.sort()
        if list_buff != list_chan :
            pos += 1
            button = NewButton('⬇  Download message buffer', self.Telegram_ui.fill_msg_buffer)
            self.chan_list.insert(pos, button)


        self.focus_position = current_pos

    def add_msg(self, cmd, incr):
        """ unread message count incrementation
        """
        if incr:
            if cmd in self.msg_chan:
                self.msg_chan[cmd] = self.msg_chan[cmd] + 1
            else:
                self.msg_chan[cmd] = 1
        else:
            self.msg_chan[cmd] = 0

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

        #save previous messages
        prev_cmd = self.Telegram_ui.current_chan.entity.id
        prev_msg = self.Telegram_ui.msg_send_widget.widgetEdit.get_edit_text()
        self.Telegram_ui.msg_send_widget.buffer_writing_text[prev_cmd] = prev_msg

        if prev_msg and not self.Telegram_ui.NINJA_MODE:
            dst = self.Telegram_ui.current_chan['print_name']
            # try/expect needed when user lacks of priviledge on channels
            try:
                self.Telegram_ui.tg_client.send_typing_abort(dst)
            except Exception as e:
                logging.getLogger().warning("Couldn't send typing abort", exc_info=True)


        self.Telegram_ui.current_chan = chan

        current_cmd = chan[1].id

        if current_cmd not in self.Telegram_ui.last_media:
            self.Telegram_ui.last_media[current_cmd] = {}
        self.Telegram_ui.msg_widget.get_history()
        self.Telegram_ui.msg_send_widget.update_send_widget()

        # deletion of unread count for the new chan
        if current_cmd in self.msg_chan:
            del self.msg_chan[current_cmd]
        self.Telegram_ui.print_title()

        # call to refresh the current chan of the chan list
        self.update_chan_list()


        # focus on the text input widget
        self.Telegram_ui.main_columns.focus_position = 2
        self.Telegram_ui.right_side.focus_position = 1


    def keypress(self, size, key):
        key = super(ChanWidget, self).keypress(size, key)

        if key == self.Telegram_ui.conf['keymap']['down']:
            self.keypress(size, 'down')
        elif key == self.Telegram_ui.conf['keymap']['up']:
            self.keypress(size, 'up')
        elif key == self.Telegram_ui.conf['keymap']['right']:
            self.Telegram_ui.main_columns.focus_position = 2
        else:
            return key



# vim: ai ts=4 sw=4 et sts=4
