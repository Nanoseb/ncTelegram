import threading
from pytg.utils import coroutine

class MessageReceiver(threading.Thread):
    def __init__(self, Telegram_ui):
        threading.Thread.__init__(self)
        self.Telegram_ui = Telegram_ui
        self.stopper = False

    def run(self):
        self.Telegram_ui.receiver.message(self.get_dump())

    def stop(self):
        self.stopper = True

    @coroutine
    def get_dump(self):
        while not self.stopper:
            msg = (yield)

            #si c'est un message on l'affiche
            if msg['event'] == "message":
                current_cmd = self.Telegram_ui.current_chan['type'] + "#" + str(self.Telegram_ui.current_chan['id']) 

                try:
                    # vérifie que le message a été envoyé au chan courant
                    if msg['receiver']['cmd'] == current_cmd and msg['peer'] == None or \
                            msg['peer']['cmd'] == current_cmd :
                        self.Telegram_ui.msg_widget.print_msg(msg)
                except:
                    print(msg)









# vim: ai ts=4 sw=4 et sts=4
