#!/usr/bin/python

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.listview import ListView
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.uix.popup import Popup
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListView, ListItemButton


import os
import state_handler
import ioup

import androidhelper
droid          = androidhelper.Android()


class TitleBar(BoxLayout):

    def __init__(self, **kwargs):
        super(TitleBar, self).__init__(**kwargs)


class MainMenu(BoxLayout):

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)


class ServerKey(BoxLayout):

    def __init__(self, **kwargs):
        super(ServerKey, self).__init__(**kwargs)


class uploadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class DataItem(object):
    def __init__(self, text='', is_selected=False):
        self.text = text
        self.is_selected = is_selected


class MainScreen(BoxLayout):
    list_adapter = ListAdapter(data="",cls=ListItemButton)
    list_view = ListView()
    _popup = Popup()
    counter = 0

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'

        """
        create the manager
        """
        self.sm = ScreenManager(transition=RiseInTransition())


        """
        create a few screens
        """
        self.mainMenu   = Screen(name='mainMenu')
        self.serverKey  = Screen(name='serverKey')
        self.listScreen = Screen(name='fileList')

        """
        the menu screen manipulations
        """
        self.menu = MainMenu()
        self.menu.serverKeyBut.bind(on_release=self.goto_serverKey)
        self.menu.uploadMainBut.bind(on_release=self.show_upload)
        self.menu.listMainBut.bind(on_release=self.show_list)


        """
        the key screen manipulations
        """
        self.key  = ServerKey()
        self.key.textKey.text = state_handler.get_token()
        self.key.saveKey.bind(on_release=self.save_key)
        self.key.cancelKey.bind(on_release=self.cancel_key)


        """
        the list screen manipulations
        """
        self.listing = BoxLayout(orientation = "vertical")

        
        sublistingMenu = BoxLayout(orientation= "horizontal", size_hint_y=0.2)

        copyBut   = Button(text="copy")
        sublistingMenu.add_widget(copyBut)
        copyBut.bind(on_release=self.copy_to_clipboard_files)

        refreshBut = Button(text="refresh")
        sublistingMenu.add_widget(refreshBut)
        refreshBut.bind(on_release=self.refresh_file_list)

        delBut = Button(text="del")
        sublistingMenu.add_widget(delBut)
        delBut.bind(on_release=self.delete_file_list)

        self.listing.add_widget(sublistingMenu)

        self.data_items = []
        for key in state_handler.get_file_list().keys():
            self.data_items.append(DataItem(text=key))

        list_item_args_converter = lambda row_index, obj: {'text': obj.text,
                                                        'size_hint_y': None,
                                                        'height': 25}

        self.list_adapter = ListAdapter(data=self.data_items,
                                args_converter=list_item_args_converter,
                                selection_mode='multiple',
                                propagate_selection_to_data=True,
                                allow_empty_selection=True,
                                cls=ListItemButton)

        self.list_view = ListView(adapter=self.list_adapter)

        self.listing.add_widget(self.list_view)

        cancelBut = Button(text= "cancel", size_hint_y=0.2)
        cancelBut.bind(on_release=self.cancel_key)
        self.listing.add_widget(cancelBut)


        """
        appending the screens to the screen manager
        """
        self.mainMenu.add_widget(self.menu)
        self.serverKey.add_widget(self.key)
        self.listScreen.add_widget(self.listing)

        self.sm.add_widget(self.mainMenu)
        self.sm.add_widget(self.serverKey)
        self.sm.add_widget(self.listScreen)


        """
        go directly to key screen if the key isn't set yet
        """
        if state_handler.get_token() == "":
            self.sm.current = 'serverKey'
        else:
            self.sm.current = 'mainMenu'


        """
        add all the widgets
        """
        title = TitleBar()
        self.add_widget(title)
        self.add_widget(self.sm)



    """
    start of callback foos
    """

    def goto_serverKey(self, object):
        self.sm.current = "serverKey"

    def save_key(self, object):
        state_handler.store_token(self.key.textKey.text)
        self.sm.current = "mainMenu"

    def cancel_key(self, object):
        self.sm.current = "mainMenu"
        self.update_list()

    def show_list(self, object):
        self.sm.current = "fileList"

    def show_upload(self, object):
        content = uploadDialog(load=self.upload, cancel=self.dismiss_popup)
        self._popup = Popup(title="Upload", content=content,size_hint=(0.9, 0.9))
        self._popup.open()


    def upload(self, path, filename):
        if len(filename) == 0:
            return
        self.dismiss_popup()
        file_name = os.path.join(path,filename[0])

        #uploading file
        result = ioup.upload_file(state_handler.get_token(), file_name)
        if result == " ":
            self.error("Cannot upload file "+file_name)
            return

        droid.setClipboard(result.encode('utf-8'))

        #updating the list
        result2 = ioup.check_list(state_handler.get_token())
        if result2 == {" ":" "}:
            self.error("Wasn't able to refresh list")
            return
        state_handler.store_file_list(result2)
        self.update_list()
        self.dismiss_popup()

        content = BoxLayout(orientation = 'vertical')
        content.add_widget(Label(text="Uploaded Successfully: \n"+file_name+"\n"+result))
        closeButton  = Button(text='OK',size_hint_y = 0.15)
        content.add_widget(closeButton)
        self._popup = Popup(title='Uploaded', content=content,size_hint=(0.8, 0.8))
        closeButton.bind(on_press=self._popup.dismiss)
        self._popup.open()


    def dismiss_popup(self):
        self.outputing = False
        self._popup.dismiss()


    def error(self, message):
        self.dismiss_popup()
        content = BoxLayout(orientation = 'vertical')
        content.add_widget(Label(text=message))
        closeButton  = Button(text='OK',size_hint_y = 0.15)
        content.add_widget(closeButton)
        self._popup = Popup(title='Error', content=content,size_hint=(0.8, 0.8))
        closeButton.bind(on_press=self._popup.dismiss)
        self._popup.open()

    def update_list(self):
        self.data_items = []
        self.counter = self.counter +1
        for key in state_handler.get_file_list().keys():
            self.data_items.append(DataItem(text=key))
        self.list_adapter.data = self.data_items
        self.list_view.adapter = self.list_adapter

    def copy_to_clipboard_files(self,object):
        clipboard_data = ""
        for data in self.data_items:
            if data.is_selected:
                clipboard_data +=  "http://pub.iotek.org/"+state_handler.get_file_list()[data.text]+"    "
        droid.setClipboard(clipboard_data.encode('utf-8'))


    def refresh_file_list(self, object):
        result = ioup.check_list(state_handler.get_token())
        if result == {" ":" "}:
            self.error("Wasn't able to refresh list")
            return
        state_handler.store_file_list(result)
        self.update_list()

    def delete_file_list(self, object):
        for data in self.data_items:
            if data.is_selected:
                result = ioup.remove_file(
                        state_handler.get_token(), 
                        state_handler.get_file_list()[data.text]
                )
                if result == False:
                    self.error("Could not remove file: \n"+ data.text)
                    return

        #updating the list
        result2 = ioup.check_list(state_handler.get_token())
        if result2 == {" ":" "}:
            self.error("Wasn't able to refresh list")
            return
        state_handler.store_file_list(result2)
        self.update_list()
        self.dismiss_popup()


class IoupApp(App):

    def build(self):
        win = MainScreen()
        Window.clearcolor = (0.15, 0.15, 0.15, 1)
        return win


if __name__ == '__main__':
  IoupApp().run()

