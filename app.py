import os
from dotenv import load_dotenv
from flask import Flask, abort, request
from datetime import datetime
# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
# pymongo
from flask.json import JSONEncoder
import pymongo
from bson import json_util
# import configparser

class MongoJSONEncoder(JSONEncoder):
    def default(self, obj): 
        return json_util.default(obj)

app = Flask(__name__)
app.json_encoder = MongoJSONEncoder

# load_dotenv()
# config = configparser.ConfigParser()
# config.read('./config.ini')
# line_bot_api = LineBotApi(config.get('line-bot', 'CHANNEL_ACCESS_TOKEN'))
# handler = WebhookHandler(config.get('line-bot', 'CHANNEL_SECRET'))
# client = pymongo.MongoClient(config.getenv('mongo', "MONGO_URI"))

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))
client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
db = client.JokeBot

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text
    if db.chat_state.find_one({ "time": "current" })["state"] == "task":
        step = db.chat_state.find_one({ "time": "current" })["step"]
        reply = db.choices.find_one({ "name": 'task'})["sys_replies"][step]
        step += 1
        if step >= len(db.choices.find_one({ "name": 'task'})["sys_replies"]):
            result = db.chat_state.update_one({ "time": "current" }, { "$set": { "state": "general", "step": 0 } })
        else:
            result = db.chat_state.update_one({ "time": "current" }, { "$set": { "state": "task", "step": step } })
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))        
    # see if there's event from rich-menu
    # choices = ['task', 'deadline', 'joke']:
    elif get_message == db.choices.find_one({ "name": 'task' })["usr_utter"]:
        result = db.chat_state.update_one({ "time": "current" }, { "$set": { "state": "task", "step": 0 } })
        reply = db.choices.find_one({ "name": 'task' })["sys_replies"][0]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))
    elif get_message == db.choices.find_one({ "name": 'dealine' })["usr_utter"]:
        result = db.chat_state.update_one({ "time": "current" }, { "$set": { "state": "deadline", "step": 0 } })
        reply = "還沒完成的事項有：\n"
        todos = ""
        for t in db.tasks.find().sort([("deadline", pymongo.ASCENDING)]):
            if not t.isFinished:
                todos += t.deadline + ' ' + t.title + '\n'
        if todos == "":
            reply = "沒有尚未完成的事項，太強了吧！！！"
        else: 
            reply += db.choices.find_one({ "name": 'dealine' }).sys_reply
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))
    elif get_message == db.choices.find_one({ "name": 'joke' }).usr_utter:
        result = db.chat_state.update_one({ "time": "current" }, { "$set": { "state": "joke", "step": 0 } })
        reply = db.jokes.find_one()["content"]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))
    
    # see if any finished task is reported
    elif get_message.find("完成了") != -1:
        result = db.chat_state.update_one({ "time": "current" }, { "$set": { "state": "general", "step": 0 } })
        task_name = get_message[:get_message.find("完成了")]
        # find task
        result = db.tasks.find_one({ "title": task_name })
        if result is None:
            reply = '確定沒打錯字？我怎麼不記得有' + task_name + '這個事項'
        else:
            result = db.tasks.update_one({ "title": task_name }, { "$set": { "isFinished": True } })
            reply = '恭喜完成' + task_name + '！你好棒～～'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))

    # general case
    else:
        result = db.chat_state.update_one({ "time": "current" }, { "$set": { "state": "general", "step": 0 } })
        reply = "嗡嗡嗡 快上工！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{reply}"))