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
        
        msgDict = self.Telegram_ui.sender.history(self.Telegram_ui.current_chan)
        msgList = []


        for field in msgDict:
            try:
                msgList.append([ field['from']['print_name'], field['text'], field['date']])
            except:
                # To handle message without text (like media)
                try:
                    msgList.append([ field['from']['print_name'], "No text", field['date']])
                except:
                    msgList.append([ "message", "ERROR", 123456]) #FIX ME : problem pour certain user

        msgList = msgList[::-1]

        for i in msgList:
            date = time.strftime('%d-%m-%Y %H:%M:%S ', time.localtime(i[2]))
            self.msg_list.insert(pos + 1, urwid.Text(date + i[0] + " -> " +i[1]))
            self.focus_position = pos + 1
        self.msgs = msgList
        self.updateLocked = False





# vim: ai ts=4 sw=4 et sts=4
