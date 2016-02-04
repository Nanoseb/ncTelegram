import urwid
import time

# Le widget utilise pour afficher la liste des messages
class MessageWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.msgs = []
        self.updateLocked = False

        self.Telegram_ui = Telegram_ui

        self.getHistory()
    

    def getHistory(self):
        while (self.updateLocked):
            time.sleep(0.5)
        self.updateLocked = True

        # Suppression des messages précédent (=redéfinition du widget)
        self.msg_list = urwid.SimpleFocusListWalker([urwid.Text(('msg', "Messages :"),align='left')]) 
        super().__init__(self.msg_list)
        pos = self.focus_position
        
        msgDict = self.Telegram_ui.sender.history(self.Telegram_ui.current_chan['print_name'])
        msgList = []

        self.pos = 1
        for msg in msgDict:
            self.print_msg(msg)


        self.updateLocked = False


    def print_msg(self, msg):
        date = 1
        sender = "unknown"
        text = "ERROR"

        try:
            date = msg['date'] 
            sender = msg['from']['print_name']
            text = msg['text']
        except:
            try:
                date = msg['date'] 
                sender = msg['sender']['first_name']
                text = msg['text']

                # To handle message without text (like media)
            except:
                try:
                    date = msg['date'] 
                    sender = msg['from']['print_name'] 
                    text = "media"
                except:
                    date = 1                   #FIX ME : problem pour certain user
                    sender = "unknown"
                    text = "ERROR"

        
        date = time.strftime('%d-%m-%Y %H:%M:%S ', time.localtime(date))

        self.msg_list.insert( self.pos +1 , urwid.Text(date + sender + " -> " + text))
        self.focus_position = self.pos 
        self.pos = self.pos +1



# vim: ai ts=4 sw=4 et sts=4
