import threading
from pytg.utils import coroutine

class MessageReceiver(threading.Thread):
    def __init__(self, Telegram_ui):
        threading.Thread.__init__(self)
        self.Telegram_ui = Telegram_ui


    def run(self):
        self.Telegram_ui.receiver.message(self.get_dump())


    @coroutine
    def get_dump(self):
        while True:
            msg = (yield)

            # si c'est un message on l'affiche
            if msg['event'] == "message":
                self.Telegram_ui.chan_widget.add_msg(msg)

                current_cmd = self.Telegram_ui.current_chan['type'] + "#" + str(self.Telegram_ui.current_chan['id']) 
                # vérifie que le message a été envoyé au chan courant
                if msg['receiver']['cmd'] == current_cmd:
                     self.Telegram_ui.msg_widget.print_msg(msg)
  
                try:
                    if self.Telegram_ui.me['username'] != '' and \
                            "@" + self.Telegram_ui.me['username'] in msg['text']:
                        self.Telegram_ui.display_notif(msg)
                except:
                    """ """

                # On actualise l'affichage 
                self.Telegram_ui.main_loop.draw_screen()
              
# vim: ai ts=4 sw=4 et sts=4
