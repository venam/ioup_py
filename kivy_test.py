from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.listview import ListView, ListItemButton
from kivy.adapters.listadapter import ListAdapter


class DataItem(object):
    def __init__(self, text='', is_selected=False):
        self.text = text
        self.is_selected = is_selected


class MainView(GridLayout):
    '''Implementation of a simple list view with 100 items.
    '''
    the_item_list = [str(index) for index in range(100)]

    def __init__(self, **kwargs):
        kwargs['cols'] = 2
        super(MainView, self).__init__(**kwargs)
        self.but = Button(text = "delete thing")
        self.but.bind(on_release=self.delete_thing)

        self.but2 = Button(text = "2")
        self.but2.bind(on_release=self.gototwo)

        # Create the manager
        self.sm = ScreenManager(transition = FadeTransition())
        # Add few screens
        self.screen  = Screen(name='one')
        self.screen.add_widget(Button(text="hello"))
        self.screen2 = Screen(name='two')
        self.screen2.add_widget(Button(text="world"))
        self.sm.add_widget(self.screen)
        self.sm.add_widget(self.screen2)


        data_items = []
        data_items.append(DataItem(text='cat'))
        data_items.append(DataItem(text='dog'))
        data_items.append(DataItem(text='frog'))

        list_item_args_converter = lambda row_index, obj: {'text': obj.text,
                                                        'size_hint_y': None,
                                                        'height': 25}

        list_adapter = ListAdapter(data=data_items,
                                args_converter=list_item_args_converter,
                                selection_mode='multiple',
                                propagate_selection_to_data=True,
                                allow_empty_selection=False,
                                cls=ListItemButton)

        list_view = ListView(adapter=list_adapter)


        # By default, the first screen added into the ScreenManager will be
        # displayed. You can then change to another screen.

        # Let's display the screen named 'Title 2'
        # A transition will automatically be used.
        self.sm.current = 'one'

        #self.list_view = ListView(item_strings=self.the_item_list)
        self.add_widget(self.but)
        self.add_widget(list_view)
        self.add_widget(self.but2)
        self.add_widget(self.sm)

    def delete_thing(self,object):
        if len(self.the_item_list)>1:
            del(self.the_item_list[0])
            self.list_view.item_strings = self.the_item_list
            print "ok"
        else:
            print "no"

    def gototwo(self,object):
        self.sm.current = 'two'


if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(MainView(width=800))


