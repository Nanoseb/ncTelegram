import urwid
import time

# Le widget utilise pour afficher la liste des chans
class ChanWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.chans = []
        self.updateLocked = False
        self.chan_list = urwid.SimpleFocusListWalker([urwid.Text("Chan"), urwid.Divider()])
        super().__init__(self.chan_list)
        self.updateChanList(Telegram_ui)
    
    # Mettre a jour la liste des chans
    def updateChanList(self, Telegram_ui):
        while (self.updateLocked):
            time.sleep(0.5)
        self.updateLocked = True
        #self.chan_list.set_text("Chans :")
        dict = Telegram_ui.sender.dialog_list()
        chanList = [ [name['print_name'], name['print_name'], name['type']] for name in dict ][::-1]
        pos = self.focus_position
        for i in chanList:
            button = urwid.Button(i[1] + ": " + i[2])
            urwid.connect_signal(button, 'click', self.chan_chosen, i[0])
            self.chan_list.insert(pos + 1, urwid.AttrMap(button, None, focus_map='reversed'))
            pos = pos + 1
            #self.chan_list.set_text(self.chan_list.text 
            #+ u"\n→ " + i[0] + ": " + i[1])
        self.chans = chanList
        self.updateLocked = False

    def chan_chosen(self, button, print_name):
        return ok



# vim: ai ts=4 sw=4 et sts=4
