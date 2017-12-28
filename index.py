from flask import Flask, request as something, abort
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
from timeout import Timeout
from ProgramTerminated import ProgramTerminated
from InputSection import InputSection,EnterInput

app = Flask(__name__)
load_dotenv(find_dotenv())
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))
client = Wit(os.environ.get('WIT_ACCESS_TOKEN'))

del os
del load_dotenv,find_dotenv

def composed(*decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return deco

@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = something.headers['X-Line-Signature']
    # get request body as text
    body = something.get_data(as_text=True)
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

def open(*args,**kwargs):
    raise IOError

def dir(*args,**kwargs):
    raise IOError

@composed(handler.add(MessageEvent, message=TextMessage))
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    id = str(profile.user_id)
    if(id not in EnterInput.user_input):
        EnterInput.user_input[id]=[]
        
    if(id not in EnterInput.input):
        EnterInput.input[id] = False
    
    if(EnterInput.input[id]):
        get_message = event.message.text
        case = get_message.split("\n")
        EnterInput.user_input[id] = case[:]
        EnterInput.input[id] = False
        reply_message = TextSendMessage(text="Now enter your program")
    
    else:

        def input(str="",*args,**kwargs):
            if(EnterInput.user_input):
                return EnterInput.user_input[id].pop(0)
            else:
                raise InputSection

        _restricted_modules = ['os','subprocess','requests','tkinter','Tkinter','environ','inspect','dotenv']
        for i in _restricted_modules:
            sys.modules[i] = None
        get_message = event.message.text
        if(get_message == "/help"):
            reply_message = TextSendMessage(text="You can run simple python program just by write the code here. To add user input, type /input in this chat and enter the input.")
        elif(get_message == "/about"):
            reply_message = TextSendMessage(text="Lython v.0.2.1")
        elif(get_message == "/options"):
            reply_message = TemplateSendMessage(alt_text='Message not supported',
            template=ButtonsTemplate(title='Menu',text='Please select action',
            actions=[MessageTemplateAction(label='Help',text='/help'),
            MessageTemplateAction(label='About',text='/about'),MessageTemplateAction(label="Input",text='/input')]))
        elif(get_message == "/input"):
            reply_message = TextSendMessage(text="Enter your input")
            EnterInput.input[id] = True
        else:
            try:
                with stdoutIO() as s, Timeout(3):
                    exec(get_message)
                    message = s.getvalue()
                    EnterInput.user_input[id] = []
                    if(len(message)>2000):
                        reply_message = TextSendMessage(text="This bot cannot reply with more than 2000 characters yet :(")
                    else:
                        reply_message = TextSendMessage(text=message)
            except SystemExit:
                err = "Don't go :'("
                reply_message = TextSendMessage(text=err)
            except InputSection:
                reply_message = TextSendMessage(text="Input are none or insuficcient. Use /input to add user input")
            except: 
                err = "{} occurred".format(sys.exc_info()[0].__name__)
                reply_message = TextSendMessage(text=err)
    line_bot_api.reply_message(event.reply_token,reply_message)    

if __name__ == "__main__":
    app.run()
