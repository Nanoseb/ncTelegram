import urwid
import time

# Le widget utilise pour afficher la liste des chans
class ChanWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.chans = []
        self.updateLocked = False
        self.Telegram_ui = Telegram_ui

        #self.chan_list = urwid.SimpleFocusListWalker([urwid.Text("Chan"), urwid.Divider()])
        #super().__init__(self.chan_list)
        
        self.updateChanList()
    
    # Mettre a jour la liste des chans
    def updateChanList(self):
        while (self.updateLocked):
            time.sleep(0.5)
        self.updateLocked = True

        # Réécriture de la liste, pour actualiser le chan courant
        self.chan_list = urwid.SimpleFocusListWalker([urwid.Text("Chan"), urwid.Divider()])
        super().__init__(self.chan_list)


        dict = self.Telegram_ui.sender.dialog_list()
        chanList = [ [name['print_name'], name['print_name'], name['type']] for name in dict ][::-1]
        if self.Telegram_ui.current_chan == "":
            self.Telegram_ui.current_chan = chanList[0][0]

        pos = self.focus_position
        for i in chanList:

            if i[1] == self.Telegram_ui.current_chan :            
                button = urwid.Button(i[1] + ": " + i[2] + "*")
            else:
                button = urwid.Button(i[1] + ": " + i[2])
    
            urwid.connect_signal(button, 'click', self.chan_change, i[0])
            self.chan_list.insert(pos + 1, urwid.AttrMap(button, None, focus_map='reversed'))
            pos = pos + 1


        self.chans = chanList
        self.updateLocked = False

    def chan_change(self, button, print_name): 
       
        # On actualise les autres widgets
        self.Telegram_ui.current_chan = print_name
        self.Telegram_ui.msg_send_widget.update_send_widget()
        self.Telegram_ui.msg_widget.getHistory()

        #Appel pour actualiser le chan courant de la liste
        self.updateChanList()


# vim: ai ts=4 sw=4 et sts=4
