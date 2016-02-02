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

        # Réécriture de la liste, pour actualiser le chan courant
        self.chan_list = urwid.SimpleFocusListWalker([urwid.Text("Chan"), urwid.Divider()])
        super().__init__(self.chan_list)


        dict = Telegram_ui.sender.dialog_list()
        chanList = [ [name['print_name'], name['print_name'], name['type']] for name in dict ][::-1]
        if Telegram_ui.current_chan == "":
            Telegram_ui.current_chan = chanList[0][0]

        pos = self.focus_position
        for i in chanList:

            if i[1] == Telegram_ui.current_chan :            
                button = urwid.Button(i[1] + ": " + i[2] + "*")
            else:
                button = urwid.Button(i[1] + ": " + i[2])
    
            urwid.connect_signal(button, 'click', self.chan_chosen, [i[0], Telegram_ui])
            self.chan_list.insert(pos + 1, urwid.AttrMap(button, None, focus_map='reversed'))
            pos = pos + 1


        self.chans = chanList
        self.updateLocked = False

    def chan_chosen(self,salut, list_arg): #print_name, Telegram_ui):
        print_name = list_arg[0]
        Telegram_ui = list_arg[1]
        
        Telegram_ui.current_chan = print_name
        Telegram_ui.msg_widget.getHistory(Telegram_ui)

        #Appel pour actualiser le chan courant
        self.updateChanList(Telegram_ui)


# vim: ai ts=4 sw=4 et sts=4
