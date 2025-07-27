import sys
import asyncio
import discord
from PyQt5 import QtWidgets, QtGui, QtCore
from discord.ext import tasks
from PyQt5.QtCore import QMetaObject, Qt

class DiscordBotClient(discord.Client):
    def __init__(self, app, token, activity):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.app = app
        self.token = token
        self.activity_str = activity

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.change_presence(activity=discord.Game(name=self.activity_str))
        self.app.populate_guilds(self.guilds)

    async def on_message(self, message):
        if message.channel.id == self.app.current_channel_id:
            self.app.append_message(f"<b>{message.author.display_name}</b>: {message.content}")

class BotApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Discord Bot Client")
        self.setGeometry(100, 100, 1000, 600)
        self.token = ""
        self.activity = ""
        self.current_channel_id = None
        self.client = None
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout()

        self.server_list = QtWidgets.QListWidget()
        self.server_list.setFixedWidth(100) 
        self.server_list.setSpacing(15)  
        self.server_list.setStyleSheet("""
            QListWidget {
                background-color: #2f3136;
                border: none;
                padding: 10px;
                border-radius: 8px;
                padding-top: 20px;
                padding-bottom: 20px;
            }
            QListWidget::item {
                background-color: #5865f2;
                margin: 8px;
                border-radius: 24px;
                height: 60px;
                text-align: center;
                color: white;
                font-size: 18px;
                padding: 12px;
                transition: background-color 0.3s ease;
            }
            QListWidget::item:hover {
                background-color: #4752c4;
            }
            QListWidget::item:selected {
                background-color: #4752c4;
            }
        """)
        self.server_list.currentRowChanged.connect(self.on_guild_selected)
        main_layout.addWidget(self.server_list)

        # Channel selector (same as before)
        self.channel_selector = QtWidgets.QListWidget()
        self.channel_selector.setFixedWidth(200)
        self.channel_selector.setStyleSheet("""
            QListWidget {
                background-color: #2f3136;
                border: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                color: #b9bbbe;
            }
            QListWidget::item:selected {
                background-color: #4f545c;
                color: white;
            }
        """)
        self.channel_selector.currentRowChanged.connect(self.on_channel_selected)
        main_layout.addWidget(self.channel_selector)

        chat_layout = QtWidgets.QVBoxLayout()

        self.messages_display = QtWidgets.QTextBrowser()
        self.messages_display.setStyleSheet("background-color: #36393f; border: none; color: #dcddde; padding: 10px;")
        chat_layout.addWidget(self.messages_display)

        self.message_input = QtWidgets.QLineEdit()
        self.message_input.setPlaceholderText("Message #channel-name")
        self.message_input.returnPressed.connect(self.send_message)
        chat_layout.addWidget(self.message_input)

        chat_widget = QtWidgets.QWidget()
        chat_widget.setLayout(chat_layout)
        main_layout.addWidget(chat_widget)

        self.token_input = QtWidgets.QLineEdit()
        self.token_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.token_input.setPlaceholderText("Bot Token")

        self.status_input = QtWidgets.QLineEdit()
        self.status_input.setPlaceholderText("Bot Status")

        self.connect_button = QtWidgets.QPushButton("Connect Bot")
        self.connect_button.clicked.connect(self.start_bot)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.token_input)
        top_layout.addWidget(self.status_input)
        top_layout.addWidget(self.connect_button)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.addLayout(top_layout)
        layout.addLayout(main_layout)

        self.setCentralWidget(container)

        # Global stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #36393f;
                color: #dcddde;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #40444b;
                border: 1px solid #202225;
                border-radius: 6px;
                padding: 6px;
                color: white;
            }
            QLineEdit:focus {
                border-color: #5865f2;
            }
            QPushButton {
                background-color: #5865f2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
        """)

    def start_bot(self):
        self.token = self.token_input.text().strip()
        self.activity = self.status_input.text().strip()

        if not self.token:
            QtWidgets.QMessageBox.critical(self, "Token Missing", "Please enter a bot token.")
            return

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self.client = DiscordBotClient(self, self.token, self.activity)

        self.thread = QtCore.QThread()
        self.worker = DiscordWorker(self.client, self.token)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def populate_guilds(self, guilds):
        self.guilds = guilds
        self.server_list.clear()
        for g in guilds:
            item = QtWidgets.QListWidgetItem(g.name[0])  
            self.server_list.addItem(item)

    def on_guild_selected(self, index):
        guild = self.guilds[index]
        self.channels = [c for c in guild.text_channels if c.permissions_for(guild.me).read_messages]
        self.channel_selector.clear()
        for ch in self.channels:
            self.channel_selector.addItem(f"#{ch.name}")

    def on_channel_selected(self, index):
        if index >= 0:
            channel = self.channels[index]
            self.current_channel_id = channel.id
            self.messages_display.clear()
            asyncio.run_coroutine_threadsafe(self.load_messages(channel), self.client.loop)

    async def load_messages(self, channel):
        try:
            async for msg in channel.history(limit=50):
                self.append_message(f"<b>{msg.author.display_name}</b>: {msg.content}")
        except discord.Forbidden:
            self.append_message("<i>[System]</i> Cannot read message history in this channel.")

    def append_message(self, text):
        QMetaObject.invokeMethod(self.messages_display, "append", Qt.QueuedConnection, QtCore.Q_ARG(str, text))

    def send_message(self):
        text = self.message_input.text().strip()
        if text and self.current_channel_id:
            channel = self.client.get_channel(self.current_channel_id)
            if channel:
                asyncio.run_coroutine_threadsafe(channel.send(text), self.client.loop)
                self.message_input.clear()

class DiscordWorker(QtCore.QObject):
    def __init__(self, client, token):
        super().__init__()
        self.client = client
        self.token = token

    def run(self):
        try:
            asyncio.run(self.client.start(self.token))
        except discord.LoginFailure:
            QtWidgets.QMessageBox.critical(None, "Login Failed", "Invalid token.")
            QtCore.QCoreApplication.quit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Error", str(e))
            QtCore.QCoreApplication.quit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    bot_app = BotApp()
    bot_app.show()
    sys.exit(app.exec_())
