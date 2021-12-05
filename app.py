import os
from flask import Flask, abort, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import (
    RichMenu,
    RichMenuArea,
    RichMenuSize,
    RichMenuBounds,
    URIAction
)
from linebot.models.actions import RichMenuSwitchAction
from linebot.models.rich_menu import RichMenuAlias

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


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

##############
## messages ##
##############
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text

    # Send To Line
    reply = TextSendMessage(text=f"{get_message}")
    line_bot_api.reply_message(event.reply_token, reply)

###############
## rich menu ##
###############

# def rich_menu_object_a_json():
#     return {
#         "size": {
#             "width": 2500,
#             "height": 1686
#         },
#         "selected": False,
#         "name": "richmenu-a",
#         "chatBarText": "Tap to open",
#         "areas": [
#             {
#                 "bounds": {
#                     "x": 0,
#                     "y": 0,
#                     "width": 1250,
#                     "height": 1686
#                 },
#                 "action": {
#                     "type": "uri",
#                     "uri": "https://www.line-community.me/"
#                 }
#             },
#             {
#                 "bounds": {
#                     "x": 1251,
#                     "y": 0,
#                     "width": 1250,
#                     "height": 1686
#                 },
#                 "action": {
#                     "type": "uri",
#                     "uri": "https://www.facebook.com/"
#                 }
#             }
#         ]
#     }


# def create_action(action):
#     if action['type'] == 'uri':
#         return URIAction(type=action['type'], uri=action.get('uri'))


# def main():
#     # 2. Create rich menu A (richmenu-a)
#     rich_menu_object_a = rich_menu_object_a_json()
#     areas = [
#         RichMenuArea(
#             bounds=RichMenuBounds(
#                 x=info['bounds']['x'],
#                 y=info['bounds']['y'],
#                 width=info['bounds']['width'],
#                 height=info['bounds']['height']
#             ),
#             action=create_action(info['action'])
#         ) for info in rich_menu_object_a['areas']
#     ]

#     rich_menu_to_a_create = RichMenu(
#         size=RichMenuSize(width=rich_menu_object_a['size']['width'], height=rich_menu_object_a['size']['height']),
#         selected=rich_menu_object_a['selected'],
#         name=rich_menu_object_a['name'],
#         chat_bar_text=rich_menu_object_a['name'],
#         areas=areas
#     )

#     rich_menu_a_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_a_create)

#     # 3. Upload image to rich menu A
#     with open('./img/richmenu-a.png', 'rb') as f:
#         line_bot_api.set_rich_menu_image(rich_menu_a_id, 'image/png', f)

#     print('success')


# main()