\# Discord Bot Client GUI



A modern GUI-based Discord bot client built using \*\*PyQt5\*\* and \*\*discord.py\*\*, enabling easy control over your bot, server and channel selection, and live message streaming and sending — all from a beautiful desktop interface.



---



\## 📦 Features



\- 🔐 Secure bot token input with GUI feedback.

\- 🎮 Custom bot activity (status) support.

\- 🌐 Server and channel browser sidebar.

\- 💬 Live message feed from selected text channel.

\- ✉️ Send messages directly from the GUI.

\- ⚙️ Discord bot lifecycle management with async/threaded support.

\- 🧊 Clean, Discord-like UI theme via Qt stylesheets.



---



\## 🚀 Getting Started



\### 1. Clone the Repository



```bash

git clone https://github.com/17xet/discord-bot-client.git

cd discord-bot-client

````



\### 2. Install Dependencies



Use pip and preferably a virtual environment:



```bash

pip install -r requirements.txt

```



\### 3. Run the App



```bash

python main.py

```



---



\## 🛠 Requirements



\* Python 3.8+

\* PyQt5

\* discord.py (v2.0+)



Install manually (if not using `requirements.txt`):



```bash

pip install pyqt5 discord.py

```



---



\## 🖼️ Screenshot



> \*\<img width="1000" height="630" alt="Preview" src="https://github.com/user-attachments/assets/14a1de4f-0a90-4dd5-8010-1dd475309bff"/>*



---



\## 🔐 Security Note



\* The bot token is never stored or logged.

\* GUI prevents running the bot without a valid token.



---



\## 📁 File Structure



```plaintext

.

├── main.py              # Main entry point

├── README.md

├── requirements.txt     # Python dependencies

└── .gitignore

```

