#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urwid


class PopUp(urwid.PopUpLauncher):
    def __init__(self, widgetbase, widgetpop):
        self.__super.__init__(widgetbase)
        urwid.connect_signal(self.original_widget, 'click',
            lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = PopUpDialog()
        urwid.connect_signal(pop_up, 'close',
            lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left':0, 'top':1, 'overlay_width':32, 'overlay_height':7}






















# vim: ai ts=4 sw=4 et sts=4
