# -*- coding: utf-8 -*-
import urwid
from pytg.receiver import Receiver
from pytg.utils import coroutine

def question():
    return urwid.Pile([urwid.Edit(('I say', u"What is your name?\n"))])

@coroutine
def example_function(receiver):
        print(456)
        msg = (yield)
        print(str(msg))
        return urwid.Text(('I say', str(msg)))


class ConversationListBox(urwid.ListBox):
    def __init__(self):
        body = urwid.SimpleFocusListWalker([question()])
        super(ConversationListBox, self).__init__(body)

   
    def keypress(self, size, key):
        print(123)
        # replace or add response
        example_function(receiver)
        #self.focus.contents[1:] = [(example_function(receiver), self.focus.options())]
        #pos = self.focus_position
    


if __name__ == '__main__':
        receiver = Receiver(port=4458) #get a Receiver Connector instance
        palette = [('I say', 'default,bold', 'default'),]
        receiver.start() #start the Connector.
        receiver.message(urwid.MainLoop(ConversationListBox(), palette).run())

        # continues here, after exiting while loop in example_function()
        receiver.stop()
