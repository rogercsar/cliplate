import sys
import win32clipboard as clipboard
import win32con
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLabel, QAction, QMenuBar
from PyQt5.QtGui import QIcon
from googletrans import Translator
from PyQt5.QtCore import QTimer, Qt
import pyttsx3

class ClipboardMonitor:
    def __init__(self):
        self.old_text = ""

    def get_clipboard_text(self):
        text = ""
        try:
            clipboard.OpenClipboard()
            if clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            elif clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                text = clipboard.GetClipboardData(win32con.CF_TEXT).decode('latin-1')
        except Exception as e:
            print(f"Erro ao acessar o clipboard: {e}")
        finally:
            clipboard.CloseClipboard()
        return text

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.prev_text = ""
        self.clipboard_monitor = ClipboardMonitor()
        self.translator = Translator()
        self.tts_engine = pyttsx3.init()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(1000)  # Verifica a cada 1 segundo

    def initUI(self):
        self.setWindowTitle('Cliplate')
        self.setWindowIcon(QIcon('cliplate.ico'))  # Definindo o ícone da janela

        # Configurando o layout
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.textChanged.connect(self.update_count)  # Atualiza a contagem ao mudar o texto

        # Configurando o botão TTS
        self.tts_button = QPushButton('Falar Texto', self)
        self.tts_button.clicked.connect(self.on_tts_button_click)
        self.tts_button.setStyleSheet("""
            QPushButton {
                border-radius: 50px;
                background-color: #ee4a79;
                color: white;
                border: none;
                padding: 5px;
                width: 30px;
                height: 30px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d3285a;
            }
        """)

        # Configurando o rótulo de contagem
        self.count_label = QLabel(self)
        self.count_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.update_count()  # Atualiza a contagem inicial

        # Layout do botão, área de texto e rótulo de contagem
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.tts_button)  # Adiciona o botão na parte inferior
        layout.addWidget(self.count_label)  # Adiciona o rótulo de contagem na parte inferior direita

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Configurando a barra de menu
        menubar = self.menuBar()
        format_menu = menubar.addMenu('Formatação')

        # Opções de idiomas
        lang_menu = menubar.addMenu('Idioma')
        self.lang_map = {'Inglês': 'en', 'Português': 'pt', 'Espanhol': 'es', 'Francês': 'fr', 'Alemão': 'de'}
        self.selected_lang = 'en'  # Idioma padrão
        for lang_name, lang_code in self.lang_map.items():
            lang_action = QAction(lang_name, self)
            lang_action.triggered.connect(lambda checked, l=lang_code: self.set_language(l))
            lang_menu.addAction(lang_action)

        # Adiciona o botão TTS ao menu
        #tts_action = QAction(QIcon('tts_icon.png'), 'Falar Texto', self)
        #tts_action.triggered.connect(self.on_tts_button_click)
        #menubar.addAction(tts_action)

        # Opções de fontes
        fonts = ['Arial', 'Times New Roman', 'Courier New', 'Verdana']
        for f in fonts:
            font_action = QAction(f, self)
            font_action.triggered.connect(lambda checked, f=f: self.set_font(f))
            format_menu.addAction(font_action)

    def set_font(self, font_name):
        self.text_edit.setFontFamily(font_name)

    def set_language(self, lang_code):
        self.selected_lang = lang_code
        print(f"Idioma selecionado: {lang_code}")

    def check_clipboard(self):
        try:
            text = self.clipboard_monitor.get_clipboard_text()
            if text != self.prev_text:
                if text:  # Verifica se o texto não está vazio
                    self.prev_text = text
                    self.translate_text(text)
        except Exception as e:
            print(f"Erro ao verificar o clipboard: {e}")

    def translate_text(self, text):
        if self.selected_lang:
            try:
                translated = self.translator.translate(text, dest=self.selected_lang)
                translated_text = translated.text
                self.text_edit.setText(translated_text)
            except Exception as e:
                print(f"Erro na tradução: {e}")

    def on_tts_button_click(self):
        text = self.text_edit.toPlainText()
        if text:
            self.text_to_speech(text)

    def text_to_speech(self, text):
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Erro na conversão de texto para fala: {e}")

    def update_count(self):
        text = self.text_edit.toPlainText()
        lines = text.count('\n') + 1  # Conta o número de linhas
        chars = len(text)
        self.count_label.setText(f"L: {lines} C: {chars}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = TranslatorApp()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Erro na aplicação: {e}")
