#!/usr/bin/env python3

from time import sleep
from threading import Thread
from getpass import getpass
import sys
import logging

from telethon import TelegramClient, sync
from telethon.errors import SessionPasswordNeededError, PhoneNumberUnoccupiedError
import telethon.tl.types as ttt
from telethon.utils import get_display_name


API_ID = "77412"
API_HASH = "9aefe703d2d5d93af30471621a550b8b"

logger = logging.getLogger(__name__)


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

# TODO: go in full async mode and get rid of the thread
class TgClient(Thread):
    """
    Abstraction over a telethon TelegramClient.
    Run in a separate thread for now
    """
    def __init__(self, Telegram_ui):
        super().__init__()
        self.Telegram_ui = Telegram_ui
        api_id = API_ID
        api_hash = API_HASH

        # TODO: put session in an appropriate folder
        self.client = TelegramClient("sessionfile", api_id, api_hash)
        print('Connecting to Telegram servers...')

        self.client.start()

        print("Connected !")
        self.client.add_event_handler(self.update_handler)

    def run(self):
        self.client.run_until_disconnected()

    def dialog_list(self,*args, **kwargs):
        # Return a list of Dialogs
        return self.client.get_dialogs(*args, **kwargs)


    def send_typing(self, *args, **kwargs):
        """
        Send "XXX is typing" notification
        """
        # TODO: invoke() the right method
        logger.error("send_typing is still undefined")

    def send_typing_abort(self, *args, **kwargs):
        """
        Stops "XXX is typing" notification
        """
        # TODO: invoke() the right method
        logger.error("send_typing_abort is still undefined")

    def status_online(self, *args, **kwargs):
        """
        Sends a "XXX is online" notification
        """
        # TODO: invoke() the right method
        logger.error("status_online is still undefined")

    def status_offline(self, *args, **kwargs):
        """
        Sends a "XXX is offline" notification
        """
        # TODO: invoke() the right method
        logger.error("status_offline is still undefined")

    def mark_read(self, *args, **kwargs):
        """
        Marks messages as read
        """
        # TODO: invoke() the right method

    def send_file(self, *args, **kwargs):
        """
        Send a file
        """
        # TODO: invoke() the right method

    def history(self, entity, *args, **kwargs):
        return self.client.get_messages(entity, *args, **kwargs)

    def update_handler(self, update_object):
        if self.Telegram_ui.lock_receiver:
            logger.warning("update_handler called, but receiver locked")
            return

        current_cmd = self.Telegram_ui.current_chan.id
        logger.info("Got update %s", update_object)

        if isinstance(update_object, ttt.UpdateShortMessage):
            # TODO: differenciate sender == me
            #msg_type = msg['receiver']['type']
            #if msg_type == 'user' and not msg['own']:
            #    msg_cmd = msg['sender']['id']
            #else:
            #    msg_cmd = msg['receiver']['id']
            msg = update_object.message
            msg_cmd = update_object.user_id

            if update_object.date.timestamp() < self.Telegram_ui.boot_time:
                if not msg.media_unread: # TODO: rewrite this check
                    return
                self.Telegram_ui.chan_widget.add_msg(msg_cmd, True)
                self.Telegram_ui.chan_widget.update_chan_list()
                self.Telegram_ui.main_loop.draw_screen()
                return

            msg_id = update_object.id

            # handling of unread count, message print, and buffer fill
            if msg_cmd == current_cmd:
                self.Telegram_ui.msg_widget.print_msg(update_object)
                self.Telegram_ui.chan_widget.add_msg(msg_cmd, False)

            # TODO: handle this case
            #elif ('from' in msg and msg['from']['peer_id'] == self.Telegram_ui.me['id']) or \
            #    ('sender' in msg and msg['sender']['id'] == self.Telegram_ui.me['id']):
            #    # mark message as read if the message is from you
            #    if msg_cmd in self.Telegram_ui.chan_widget.msg_chan:
            #        del self.Telegram_ui.chan_widget.msg_chan[msg_cmd]
            #        self.Telegram_ui.print_title()
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
                msg_reply = self.Telegram_ui.tg_client.message_get(msg['reply_id'])
                if ('from' in msg_reply and\
                        msg_reply['from']['id'] == self.Telegram_ui.me['id']) or \
                        ('sender' in msg_reply and\
                         msg_reply['sender']['id'] == self.Telegram_ui.me['id']):
                    self.Telegram_ui.display_notif(msg)



            self.Telegram_ui.update_read_status(msg_cmd, False)

            # refresh of the screen
            self.Telegram_ui.main_loop.draw_screen()



        elif isinstance(update_object, ttt.UpdateUserStatus):
            status = update_object.status
            if isinstance(status, ttt.UserStatusOnline):
                when = str(status.expires)
                status = True
            elif isinstance(status, ttt.UserStatusOffline):
                when = str(status.was_online)
                status = False
            else:
                raise NotImplementedError("Missing case for update", update_object)
            self.Telegram_ui.update_online_status(when, status, update_object.user_id)



        elif isinstance(update_object, ttt.UpdateReadHistoryInbox):
            peer = update_object.peer
            if isinstance(peer, ttt.PeerChannel):
                cmd = peer.channel_id
            elif isinstance(peer, ttt.PeerChat):
                cmd = peer.chat_id
            else:
                assert isinstance(peer, ttt.PeerUser)
                cmd = peer.user_id
            self.Telegram_ui.update_read_status(cmd, True)

        else:
            logger.warning("Unhandled update type %s", update_object)


# vim: ai ts=4 sw=4 et sts=4
