from flask import Flask, request
import requests
import os
from openai import OpenAI

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json

    if body and "events" in body:
        for event in body["events"]:
            if event["type"] == "message" and event["message"]["type"] == "text":
                user_text = event["message"]["text"]
                reply_token = event["replyToken"]

                # 新版 OpenAI 呼叫
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一個北海道旅遊專業顧問，專門推薦北海道一日遊與兩日遊行程。"
                        },
                        {
                            "role": "user",
                            "content": user_text
                        }
                    ]
                )

                reply_text = response.choices[0].message.content

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
                }

                data = {
                    "replyToken": reply_token,
                    "messages": [
                        {
                            "type": "text",
                            "text": reply_text[:1000]
                        }
                    ]
                }

                requests.post(
                    "https://api.line.me/v2/bot/message/reply",
                    headers=headers,
                    json=data
                )

    return "OK"


@app.route("/")
def home():
    return "LINE AI Bot is running"
