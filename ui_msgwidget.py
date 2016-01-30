import urwid
import time

# Le widget utilise pour afficher la liste des messages
class MessageWidget (urwid.Filler):
    def __init__ (self):
        self.msgs = []
        self.updateLocked = False
        
        self.msg_list = urwid.Text(('msg', "Messages :"),align='left')
        self.msg_list_attr = urwid.AttrWrap (self.msg_list, 'msg')
        super().__init__ (self.msg_list_attr, 'middle')
    
    # Mettre a jour la liste des messages
    # msgList est une liste d'éléments type [auth, msg]
    # où auth est le nom de l'auteur et msg le message
    def updateMsgList (self, msgList):
        while (self.updateLocked):
            time.sleep (0.5)
        self.updateLocked = True
        self.msg_list.set_text ("msgs :")
        for i in msgList:
            self.msg_list.set_text (self.msg_list.text 
            + "\n" + i[0] + ": " + i[1])
        self.msgs = msgList
        self.updateLocked = False





# vim: ai ts=4 sw=4 et sts=4
