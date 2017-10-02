#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess

import threading


class ThreadingRequest(threading.Thread):
    def __init__(self, Telegram_ui, run_type):
        threading.Thread.__init__(self)
        self.Telegram_ui = Telegram_ui
        self.run_type = run_type 

    def run(self):
        if self.run_type == 'mark_read':
            current_print_name = self.Telegram_ui.current_chan['print_name']
            self.Telegram_ui.sender.mark_read(current_print_name)
            self.Telegram_ui.sender.status_online()
            self.Telegram_ui.sender.status_offline()
        elif self.run_type == 'fill_buffer':
            self.fill_buffer()

    def fill_buffer(self):

        self.Telegram_ui.buffer_downloading = True

        for chan in self.Telegram_ui.chan_widget.chans[::-1]:
            cmd = chan['id']
            if cmd not in self.Telegram_ui.msg_buffer:
                print_name = chan['print_name']
                try:
                    self.Telegram_ui.msg_buffer[cmd] = self.Telegram_ui.sender.history(print_name, 50)
                except:
                    self.Telegram_ui.msg_buffer[cmd] = []
                if self.Telegram_ui.INLINE_IMAGE:
                    for msg in self.Telegram_ui.msg_buffer[cmd]:
                        if 'media' in msg:
                            image = self.Telegram_ui.msg_widget.get_inline_img(msg)

        self.Telegram_ui.buffer_downloading = False
        self.Telegram_ui.chan_widget.update_chan_list()


# vim: ai ts=4 sw=4 et sts=4
