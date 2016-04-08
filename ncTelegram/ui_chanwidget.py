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

class ChanWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.chans = []
        self.updateLocked = False
        self.current_chan_pos = 0
        self.Telegram_ui = Telegram_ui
        self.msg_chan = {}        #unread count by chan
        self.get_new_chan_list()

    def get_new_chan_list(self):
        if self.updateLocked:
            return

        self.updateLocked = True
        bool = True
        while bool:
            try:
                #list of chans
                self.chans = self.Telegram_ui.sender.dialog_list()
                bool = False
            except:
                time.sleep(0.5)
                pass

        for i in range(len(self.chans)):
            chan = self.chans[i]
            if chan['peer_type'] == 'user':
                if 'when' in chan:
                    self.Telegram_ui.online_status[chan['id']] = (chan['when'], False)
                else:
                    self.Telegram_ui.online_status[chan['id']] = ('?', False)


        self.update_chan_list()
        self.updateLocked = False


    def update_chan_list(self):

        # refresh of chan list
        self.chan_list = urwid.SimpleFocusListWalker([urwid.AttrMap(urwid.Text("Chan list:"), 'status_bar')])
        super().__init__(self.chan_list)


        if self.Telegram_ui.current_chan == []:
            self.Telegram_ui.current_chan = self.chans[-1]

        pos = self.focus_position
        
        i = len(self.chans) -1

        # build of chan list
        for chan in self.chans[::-1]:
            pos +=1
            print_name = chan['print_name']

            cmd = chan['id']

            label = print_name.replace('_', ' ')

            if chan['peer_type'] == 'user':
                label = "➜  " + label
            elif chan['peer_type'] == 'chat':
                label = "➜➜ " + label
            elif chan['peer_type'] == 'channel':
                label = "⤨  " + label

            if cmd in self.msg_chan and self.msg_chan[cmd] != 0:
                label = label + ' [' + str(self.msg_chan[cmd]) + ']'

            if print_name == self.Telegram_ui.current_chan['print_name']:
                button = NewButton(('cur_chan', label), self.chan_change, chan)
                current_pos = pos
                self.current_chan_pos = i
            else:
                button = NewButton(label, self.chan_change, chan)

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
        list_chan = [ chan['id'] for chan in self.chans ]

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
        prev_cmd = self.Telegram_ui.current_chan['id']
        prev_msg = self.Telegram_ui.msg_send_widget.widgetEdit.get_edit_text()
        self.Telegram_ui.msg_send_widget.buffer_writing_text[prev_cmd] = prev_msg
        
        if not self.Telegram_ui.NINJA_MODE:
            dst = self.Telegram_ui.current_chan['print_name']
            # try/expect needed when user lacks of priviledge on channels
            try:
                self.Telegram_ui.sender.send_typing_abort(dst)
            except:
                pass


        self.Telegram_ui.current_chan = chan

        current_cmd = chan['id']


        self.Telegram_ui.last_media = {}
        self.Telegram_ui.msg_send_widget.update_send_widget()
        self.Telegram_ui.msg_widget.get_history()

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
