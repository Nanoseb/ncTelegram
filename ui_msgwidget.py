import urwid
import time

# Le widget utilise pour afficher la liste des messages
class MessageWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.msgs = []
        self.updateLocked = False

        self.Telegram_ui = Telegram_ui
        #self.msg_list = urwid.SimpleFocusListWalker([urwid.Text(('msg', "Messages :"),align='left')]) 
        #super().__init__(self.msg_list)

        self.getHistory()
    
    # Mettre a jour la liste des messages
    # msgList est une liste d'éléments type [auth, msg]
    # où auth est le nom de l'auteur et msg le message
    def updateMsgList(self, msgList):
        while (self.updateLocked):
            time.sleep(0.5)
        self.updateLocked = True
        pos = self.focus_position
        for i in msgList:
            self.msg_list.insert(pos + 1, urwid.Text(i[0]+": "+i[1]))
            self.focus_position = pos + 1
        self.msgs = msgList
        self.updateLocked = False

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
                    test = "media"
                except:
                    date = 1                   #FIX ME : problem pour certain user
                    sender = "unknown"
                    text = "ERROR"

        
        date = time.strftime('%d-%m-%Y %H:%M:%S ', time.localtime(date))

        self.msg_list.insert( self.pos +1 , urwid.Text(date + sender + " -> " + text))
        self.focus_position = self.pos 
        self.pos = self.pos +1
        #super().__init__(self.msg_list)



# vim: ai ts=4 sw=4 et sts=4
