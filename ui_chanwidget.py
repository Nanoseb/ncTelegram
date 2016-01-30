import urwid
import time

# Le widget utilise pour afficher la liste des chans
class ChanWidget (urwid.Filler):
    def __init__ (self):
        self.chans = []
        self.updateLocked = False
        
        self.chan_list = urwid.Text(('chan', "Chans :"),align='left')
        self.chan_list_attr = urwid.AttrWrap (self.chan_list, 'chan')
        super().__init__ (self.chan_list_attr, 'middle')
    
    # Mettre a jour la liste des chans
    # chanList est une liste d'éléments type [nom, texte]
    # où nom est le nom du chan et texte un texte l'accompagnant
    def updateChanList (self, chanList):
        while (self.updateLocked):
            time.sleep (0.5)
        self.updateLocked = True
        self.chan_list.set_text ("Chans :")
        for i in chanList:
            self.chan_list.set_text (self.chan_list.text 
            + u"\n→ " + i[0] + ": " + i[1])
        self.chans = chanList
        self.updateLocked = False





# vim: ai ts=4 sw=4 et sts=4
