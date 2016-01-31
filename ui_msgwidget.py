import urwid
import time

# Le widget utilise pour afficher la liste des messages
class MessageWidget(urwid.ListBox):
    def __init__(self):
        self.msgs = []
        self.updateLocked = False
        self.msg_list = urwid.SimpleFocusListWalker([urwid.Text(('msg', "Messages :"),align='left')]) 
        super().__init__(self.msg_list)
    
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





# vim: ai ts=4 sw=4 et sts=4
