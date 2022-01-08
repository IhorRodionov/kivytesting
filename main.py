from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

import pyodbc
server = 'mysqlserver-karazinatimetable.database.windows.net'
database = 'KarazinaTimeTable'
username = 'serveradmin'
password = '{masteroftime-228}'
driver= '{ODBC Driver 17 for SQL Server}'

class MainApp(App):
    def __init__(self):
        super().__init__()
        self.input_text = TextInput(hint_text = 'Введите имя преподавателя', multiline = False)
        self.button = Button(text = "Нажми меня", on_press = self.on_press_button)
    def build(self):
        box = BoxLayout(orientation = 'vertical')
        box.add_widget(self.input_text)
        box.add_widget(self.button)
        return box

    def on_press_button(self, instance):
        connection =  pyodbc.connect('DRIVER=' + driver + ';SERVER=tcp:' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = connection.cursor()
        cursor.execute("insert into Tutors(tutor) values(?)", self.input_text.text)
        cursor.commit()


if __name__ == '__main__':
    app = MainApp()
    app.run()


