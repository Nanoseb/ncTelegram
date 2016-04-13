#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
from pytg.utils import coroutine

class MessageReceiver(threading.Thread):
    def __init__(self, Telegram_ui):
        threading.Thread.__init__(self)
        self.Telegram_ui = Telegram_ui


    def run(self):
        self.Telegram_ui.receiver.message(self.get_dump())


    @coroutine
    def get_dump(self):
        while self.Telegram_ui.lock_receiver:
            time.sleep(0.2)


        while True:
            msg = (yield)

            current_cmd = self.Telegram_ui.current_chan['id']

            if msg['event'] == "message":


                if not 'receiver' in msg:
                    continue

                msg_type = msg['receiver']['type']
                if (msg_type == 'user' or msg_type == 'encr_chat') and not msg['own']:
                    msg_cmd = msg['sender']['id']
                else:
                    msg_cmd = msg['receiver']['id']


                if msg['date'] < self.Telegram_ui.boot_time:
                    self.Telegram_ui.chan_widget.add_msg(msg_cmd, True)
                    self.Telegram_ui.chan_widget.update_chan_list()
                    self.Telegram_ui.main_loop.draw_screen()
                    continue

                msg_id = msg['id']

                # handeling of unread count, message print, and buffer fill
                if msg_cmd == current_cmd:
                    self.Telegram_ui.msg_widget.print_msg(msg)
                    self.Telegram_ui.chan_widget.add_msg(msg_cmd, False)
                else:
                    self.Telegram_ui.chan_widget.add_msg(msg_cmd, True)

                # check if the message is not already printed (by get history)
                if msg_cmd in self.Telegram_ui.msg_buffer:
                    self.Telegram_ui.msg_buffer[msg_cmd].append(msg)


                self.Telegram_ui.chan_widget.get_new_chan_list()


                # notif on hl
                if 'text' in msg and 'username' in self.Telegram_ui.me and \
                        self.Telegram_ui.me['username'] != None and\
                        "@" + self.Telegram_ui.me['username'] in msg['text']:
                    self.Telegram_ui.display_notif(msg)

                #notif on reply
                if 'reply_id' in msg and 'text' in msg:
                    msg_reply = self.Telegram_ui.sender.message_get(msg['reply_id'])
                    if ('from' in msg_reply and\
                            msg_reply['from']['id'] == self.Telegram_ui.me['id']) or \
                            ('sender' in msg_reply and\
                             msg_reply['sender']['id'] == self.Telegram_ui.me['id']):
                        self.Telegram_ui.display_notif(msg)



                self.Telegram_ui.update_read_status(msg_cmd, False)

                # refresh of the screen
                self.Telegram_ui.main_loop.draw_screen()



            elif msg['event'] == 'online-status':
                when = msg['when']
                status = msg['online']
                self.Telegram_ui.update_online_status(when, status, msg['user']['id'])



            elif msg['event'] == 'read':
                if 'receiver' in msg:
                    cmd = msg['receiver']['id']
                else:
                    cmd = msg['from']['id']
                self.Telegram_ui.update_read_status(cmd, True)

            
            elif msg['event'] == 'updates' and msg['updates'] == ['working']:
                self.Telegram_ui.chan_widget.add_secret_chat(msg)
                self.Telegram_ui.chan_widget.get_new_chan_list()
            



# vim: ai ts=4 sw=4 et sts=4
