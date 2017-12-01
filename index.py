from flask import Flask, request, abort
from dotenv import load_dotenv, find_dotenv
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,TextMessage,TextSendMessage,
    ButtonsTemplate,TemplateSendMessage,PostbackTemplateAction,
    MessageTemplateAction,URITemplateAction,
    ImageCarouselTemplate,ImageCarouselColumn)
from wit import Wit
import sys
from io import StringIO
import contextlib

app = Flask(__name__)
load_dotenv(find_dotenv())
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))
client = Wit(os.environ.get('WIT_ACCESS_TOKEN'))

@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: {}'.format(body))
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text
    if(get_message == "/help"):
        reply_message = TextSendMessage(text="You can run simple python program just by write the code here. Remember, this apps does not support user input yet.")
    elif(get_message == "/about"):
        reply_message = TextSendMessage(text="Lython v.0.1")
    elif(get_message == "/options"):
        reply_message = TemplateSendMessage(alt_text='Message not supported',
        template=ButtonsTemplate(title='Menu',text='Please select action',
        actions=[MessageTemplateAction(label='Help',text='/help'),
        MessageTemplateAction(label='About',text='/about')]))
    else:
        if('input()' not in get_message):
            try:
                with stdoutIO() as s:
                    exec(get_message)
                    reply_message = TextSendMessage(text=s.getvalue())
            except:
                reply_message = TextSendMessage(text="An error has occured")
        else:
            reply_message = TextSendMessage(text="This bot doesn't support user input yet :(")
    line_bot_api.reply_message(event.reply_token,reply_message)
        

if __name__ == "__main__":
    app.run()