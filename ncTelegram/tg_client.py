#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
from getpass import getpass

from telethon import TelegramClient, ConnectionMode
from telethon.errors import SessionPasswordNeededError, PhoneNumberUnoccupiedError
import telethon.tl.types as ttt
from telethon.utils import get_display_name

def get_print_name(entity):
    """
    Safely transforms an entity into a chat title
    """
    if isinstance(entity, ttt.User):
        if entity.username:
            return entity.username
        elif entity.first_name and entity.last_name:
            return entity.first_name + " " + entity.last_name
        elif entity.first_name or entity.last_name:
            return entity.first_name or entity.last_name
        else:
            return entity.id
    elif isinstance(entity, ttt.Channel):
        return entity.title
    elif isinstance(entity, ttt.Chat):
        return entity.title
    raise NotImplementedError("Missing case for entity", str(entity))

class TgClient(TelegramClient):
    def __init__(self, Telegram_ui):
        self.Telegram_ui = Telegram_ui
        session_user_id = Telegram_ui.conf['general']['user_login']
        api_id = Telegram_ui.conf['general']['api_id']
        api_hash = Telegram_ui.conf['general']['api_hash']
        user_phone = Telegram_ui.conf['general']['phone_number']
        super().__init__(
            session_user_id, api_id, api_hash,
            connection_mode=ConnectionMode.TCP_ABRIDGED,
            proxy=None, # TODO: add proxy objects
            update_workers=1,
            )
        print('Connecting to Telegram servers...')
        if not self.connect():
            print('Initial connection failed. Retrying...')
            if not self.connect():
                print('Could not connect to Telegram servers.')
                return
        if not self.is_user_authorized():
            # TODO: BUG, if the connection is half finished,
            # the file exists but is invalid
            self.send_code_request(user_phone)
            try:
                self.sign_in(user_phone, input('Enter code: '))
            except PhoneNumberUnoccupiedError:
                print("Please create an account first")
                exit()
            except SessionPasswordNeededError:
                print("Two factor auth detected ! Please input password")
                self.sign_in(password=getpass())
        # TODO : mettre le fichier de session dans un vrai dossier
        print("Connected !")
        self.add_update_handler(self.update_handler)

    def dialog_list(self,*args, **kwargs):
        # Renvoie une paire (dialogs, entities)
        # dialogs est la liste des "discussions" (type Dialog)
        # entities est l'entité liée à la discussion (type User, type Channel, …)
        return self.get_dialogs(*args, **kwargs)



    def update_handler(self, update_object):
        if self.Telegram_ui.lock_receiver:
            print("Warning, receiver locked")
            return

        print("Got a…", type(update_object))

        # Fetching the updates
        # (either a list of updates or an update)
        if isinstance(update_object, ttt.Updates):
            updates = [u for u in update_object.updates]
        elif isinstance(update_object, ttt.UpdateShort):
            updates = [update_object]
        else:
            print("Warning : this should not happen!")

        current_cmd = self.Telegram_ui.current_chan['id']
        print("current_cmd is", current_cmd)

        if msg['event'] == "message":


            msg_type = msg['receiver']['type']
            if msg_type == 'user' and not msg['own']:
                msg_cmd = msg['sender']['id']
            else:
                msg_cmd = msg['receiver']['id']


            if msg['date'] < self.Telegram_ui.boot_time:
                if not msg['unread']:
                    return
                self.Telegram_ui.chan_widget.add_msg(msg_cmd, True)
                self.Telegram_ui.chan_widget.update_chan_list()
                self.Telegram_ui.main_loop.draw_screen()
                return

            msg_id = msg['id']

            # handeling of unread count, message print, and buffer fill
            if msg_cmd == current_cmd:
                self.Telegram_ui.msg_widget.print_msg(msg)
                self.Telegram_ui.chan_widget.add_msg(msg_cmd, False)

            elif ('from' in msg and msg['from']['peer_id'] == self.Telegram_ui.me['id']) or \
                ('sender' in msg and msg['sender']['id'] == self.Telegram_ui.me['id']):
                # mark message as read if the message is from you
                if msg_cmd in self.Telegram_ui.chan_widget.msg_chan:
                    del self.Telegram_ui.chan_widget.msg_chan[msg_cmd]
                    self.Telegram_ui.print_title()
            else:
                self.Telegram_ui.chan_widget.add_msg(msg_cmd, True)


            # check if the message is not already printed (by get history)
            if msg_cmd in self.Telegram_ui.msg_buffer and msg_cmd != current_cmd:
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




# vim: ai ts=4 sw=4 et sts=4
