import os
from flask import Flask, abort, request, g
from flask_script import Manager
from datetime import datetime
# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import sqlite3

app = Flask(__name__)
manager = Manager(app)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))

DATABASE = "database.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def remove_db():
    if os.path.isfile(DATABASE):
        os.remove(DATABASE) 

if __name__ == '__main__':
    manager.run()

@app.route("/", methods=["GET", "POST"])
def callback():
    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"

choice_work_text='JokeBot! 準備好沒，我要交付你待辦事項了!!'
choice_ddl_text='JokeBot，一周內有哪些死線？我準備要起跑了！'
choice_joke_text='JokeBot... 我累了... 來點 Joke...'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text
    if get_message.find("完成了") != -1:
        task_name = get_message[:get_message.find("完成了")]
        # find task
        # set task.isFinished = 1
        reply = '恭喜完成' + task_name + '！你好棒～～'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))
    elif get_message == choice_work_text: 
        reply = "好，來吧！首先跟我說待辦事項標題"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))        
    elif get_message == choice_ddl_text: 
        reply = "未完成事項有：\n2021-12-8 MDS proposal\n2021-12-10 OR hw8"
        reply += "\n你再不跑快點我看是完蛋"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))
    elif get_message == choice_joke_text: 
        reply = "小明是個文藝青年，小華一直很看不慣。\n有一天小華終於受不了了，拿起防蚊液就往小明身上噴，\n.\n.\n.\n.\n.\n結果小明就變成一個普通的青年了。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))
    else:
        reply = "嗡嗡嗡 快上工！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))
    
    # Send To Line
    reply = TextSendMessage(text=f"{get_message}")
    line_bot_api.reply_message(event.reply_token, reply)