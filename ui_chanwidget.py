import urwid
import time

# Le widget utilise pour afficher la liste des chans
class ChanWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.chans = []
        self.updateLocked = False
        self.Telegram_ui = Telegram_ui
        
        self.updateChanList()
   
    # Mettre a jour la liste des chans
    def updateChanList(self):
        while (self.updateLocked):
            time.sleep(0.1)
        self.updateLocked = True

        # Réécriture de la liste, pour actualiser le chan courant
        self.chan_list = urwid.SimpleFocusListWalker([urwid.Text("Chan"), urwid.Divider()])
        super().__init__(self.chan_list)

        # list de dictionnaire contenant les chans
        self.chans = None
        while self.chans is None:
            try:
                self.chans = self.Telegram_ui.sender.dialog_list()
            except:
                time.sleep(0.5)
                pass



        if self.Telegram_ui.current_chan == []:
            self.Telegram_ui.current_chan = self.chans[-1]

        ################ Pas très propre, on peut virer la revchanList et boucler sur self.chans ##################
        pos = self.focus_position
        revchanList = [ [name['print_name'], name['print_name'], name['type']] for name in self.chans ][::-1]
        for i in revchanList:

            if i[1] == self.Telegram_ui.current_chan['print_name'] :            
                button = urwid.Button(('cur_chan', i[1].replace('_', ' ')))
                #button = urwid.Text(('cur_chan', i[1].replace('_', ' ')))
                current_pos = pos + 1
            else:
                button = urwid.Button(i[1].replace('_', ' '))
                #button = urwid.Text(i[1].replace('_', ' '))
    
            button.button_left = urwid.Text('*')
            urwid.connect_signal(button, 'click', self.chan_change, i[0])
            self.chan_list.insert(pos + 1, urwid.AttrMap(button, None, focus_map='reversed'))
            pos = pos + 1
        ###########################################################################################################

        self.focus_position = current_pos
        self.updateLocked = False

#    def keypress(self, size, key):
#        print(self.focus_position)
#        if key == 'enter':
#            pos = self.focus_position
#            self.chan_change("ui", self.chans[pos]['print_name'])
#        elif key == 'down':
#            self.focus_position = self.focus_position - 1
#        elif key == 'up':
#            self.focus_position = self.focus_position + 1

    def chan_change(self, button, print_name): 
        
        for i in self.chans:
            if i['print_name'] == print_name:
                self.Telegram_ui.current_chan = i
        

        self.Telegram_ui.msg_send_widget.update_send_widget()
        self.Telegram_ui.msg_widget.getHistory()

        #Appel pour actualiser le chan courant de la liste
        self.updateChanList()


# vim: ai ts=4 sw=4 et sts=4
