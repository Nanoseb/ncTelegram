import urwid
import time

# Le widget utilise pour afficher la liste des messages
class MessageWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.msgs = []
        self.updateLocked = False
        self.msg_list = urwid.SimpleFocusListWalker([urwid.Text(('msg', "Messages :"),align='left')]) 

        
        super().__init__(self.msg_list)
        self.getHistory(Telegram_ui)
    
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

    def getHistory(self, Telegram_ui):
        while (self.updateLocked):
            time.sleep(0.5)
        self.updateLocked = True
        pos = self.focus_position
        
        msgDict = Telegram_ui.sender.history("nc-telegram_project")
        #msgList = [ [ field['from']['print_name'], field['text'], field['date']] for field in msgDict ][::-1]
        msgList = []
        # To handle message without text (like media)
        for field in msgDict:
            try:
                msgList.append([ field['from']['print_name'], field['text'], field['date']])
            except:
                msgList.append([ field['from']['print_name'], "No text", field['date']])

        msgList = msgList[::-1]

        for i in msgList:
            date = time.strftime('%d-%m-%Y %H:%M:%S ', time.localtime(i[2]))
            self.msg_list.insert(pos + 1, urwid.Text(date + i[0] + " -> " +i[1]))
            self.focus_position = pos + 1
        self.msgs = msgList
        self.updateLocked = False





# vim: ai ts=4 sw=4 et sts=4
