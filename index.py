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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if (event.message.text == '/list'):
        reply_message = TemplateSendMessage(alt_text='Message not supported',
        template=ImageCarouselTemplate(columns=[ImageCarouselColumn(
            image_url='https://via.placeholder.com/800x800',
            action=MessageTemplateAction(label='Product 1',text='/buy product1',)),
            ImageCarouselColumn(image_url='https://via.placeholder.com/800x800',
            action=MessageTemplateAction(label='Product 2',text='/buy product2',))]))
    elif (event.message.text == '/buy product1'):
        reply_message = TextSendMessage(text='Product 1 added')
    elif (event.message.text == '/buy product2'):
        reply_message = TextSendMessage(text='Product 2 added')
    elif (event.message.text == '/who am i'):
        profile = line_bot_api.get_profile(event.source.user_id)
        reply_message = TextSendMessage(text='Name: {}\nUser ID: {}\nPicture URL: {}\nStatus: {}'.format(
            profile.display_name,profile.user_id,profile.picture_url,profile.status_message))
    elif (event.message.text == '/select'):
        reply_message = TemplateSendMessage(alt_text='Message not supported',
        template=ButtonsTemplate(title='Menu',text='Please select action',
        actions=[MessageTemplateAction(label='Say hi!',text='/hi'),
        URITemplateAction(label='Go to website',uri='http://dasardasarppw.herokuapp.com/')]))
    elif (event.message.text == '/hi'):
        reply_message = TextSendMessage(text='hi!')
    
    else:
        resp = client.message(event.message.text)
        if (resp.get('entities').get('greeting', None) != None):
            resp = resp.get('entities').get('greeting')[0]
            if resp.get('value') == 'hai':
                reply_message = TextSendMessage(text='Hai! Semoga harimu menyenangkan')
            elif resp.get('value') == 'halo':
                reply_message = TextSendMessage(text='Halo juga! Semangat buat hari ini :)')
        else:
            reply_message = TextSendMessage(text='Unknown error occured')
    line_bot_api.reply_message(event.reply_token,reply_message)
        

if __name__ == "__main__":
    app.run()