import urwid
import time

# Le widget utilise pour afficher la liste des messages
class MessageWidget(urwid.ListBox):
    def __init__(self, Telegram_ui):
        self.msgs = []
        self.updateLocked = False
        self.prev_date = 1
        self.Telegram_ui = Telegram_ui

        self.getHistory()
    

    def getHistory(self):
        while (self.updateLocked):
            time.sleep(0.5)
        self.updateLocked = True

        # Suppression des messages précédent (=redéfinition du widget)
        self.msg_list = urwid.SimpleFocusListWalker([urwid.Text(('top', " "),align='left')]) 
        super().__init__(self.msg_list)
        pos = self.focus_position
        
        msgDict = self.Telegram_ui.sender.history(self.Telegram_ui.current_chan['print_name'], 100)
        msgList = []

        self.pos = 1
        for msg in msgDict:
            self.print_msg(msg)


        self.updateLocked = False


    def print_msg(self, msg):

        try:
            date = msg['date'] 
            sender = msg['from']['print_name']
            text = msg['text']
        except:
            try:
                date = msg['date'] 
                sender = msg['sender']['first_name']
                text = msg['text']

                # To handle message without text (like media)
            except:
                try:
                    date = msg['date'] 
                    sender = msg['from']['print_name'] 
                    text = "media"
                except:
                    date = 1                   #FIX ME : problem pour certain user
                    sender = "unknown"
                    text = "ERROR"

        cur_date = time.strftime('%d/%m/%Y', time.localtime(date))

        if cur_date != self.prev_date:
            self.msg_list.insert(self.pos + 1, urwid.Text(('date', cur_date), align='center'))
            self.focus_position = self.pos 
            self.pos = self.pos +1
            self.prev_date = cur_date

        hour = time.strftime('%H:%M ', time.localtime(date))
        color = self.get_name_color(sender)
        self.msg_list.insert( self.pos +1 , urwid.Text([('hour', hour), ( color ,'{0: >10}'.format(sender)), ('light gray', " | "), text]))
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
                'dark gray',
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
