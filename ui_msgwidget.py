import urwid
import time

# Le widget utilise pour afficher la liste des messages
class MessageWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.msgs = []
        self.updateLocked = False
        self.prev_date = 1
        self.Telegram_ui = Telegram_ui
        self.fix_getHist = []
        self.getHistory()
    

    def getHistory(self):
        while (self.updateLocked):
            time.sleep(0.5)
        self.updateLocked = True
        
        # Suppression des messages précédent (=redéfinition du widget)
        self.msg_list = urwid.SimpleFocusListWalker([urwid.Text(('top', " "),align='left')]) 
        super().__init__(self.msg_list)
        pos = self.focus_position
        current_print_name = self.Telegram_ui.current_chan['print_name']

        # Hack pour fixer le problème des messages vide...
        if not current_print_name in self.fix_getHist:
            self.Telegram_ui.sender.history(current_print_name, 100)
            self.fix_getHist.append(current_print_name)

        msgDict = self.Telegram_ui.sender.history(current_print_name, 100)

        self.pos = 1
        for msg in msgDict:
            try:
                self.print_msg(msg)
            except:
                pass

        self.updateLocked = False



    def print_msg(self, msg):

        date = msg['date']
        try:
            text = msg['text']
        except:
            text = "media"

        try:
            sender = msg['from']['first_name']
        except:
            sender = msg['sender']['first_name'] 


        cur_date = time.strftime('%d/%m/%Y', time.localtime(date))

        if cur_date != self.prev_date:
            self.msg_list.insert(self.pos + 1, urwid.Text(('date', cur_date), align='center'))
            self.focus_position = self.pos 
            self.pos = self.pos +1
            self.prev_date = cur_date

        hour = time.strftime(' %H:%M ', time.localtime(date))
        color = self.get_name_color(sender + 'a')
        size_name = 9

        formated_text = text.replace(u'\n', u'\n' + ' '*(size_name + 8) + '| ')
        
        self.msg_list.insert( self.pos +1 , urwid.Text([('hour', hour),
            ( color ,'{0: >9}'.format(sender[0:size_name])),
            ('light gray', " | "),
            formated_text]))

        self.focus_position = self.pos 
        self.pos = self.pos +1

    def get_name_color(self, name):
        list_color =  ['dark red',
                'dark green',
                'brown',
                'dark blue',
                'dark magenta',
                'dark cyan',
                'light gray',
                'light red',
                'light green',
                'yellow',
                'light blue',
                'light magenta',
                'light cyan',
                'white']


        color = int(''.join(str(ord(c)) for c in name)) % len(list_color)
        return list_color[color]
        

# vim: ai ts=4 sw=4 et sts=4
