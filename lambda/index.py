# lambda/index.py
import json
import os
import re  # 正規表現モジュールをインポート
import urllib.request

LLM_API_URL = "https://ca23-35-197-132-97.ngrok-free.app/generate"


def lambda_handler(event, context):
    try:

        print("Received event:", json.dumps(event))

        # リクエストボディの解析
        body = json.loads(event["body"])
        message = body["message"]
        conversation_history = body.get("conversationHistory", [])

        print("Processing message:", message)
        print("Using model:", "External")

        # 会話履歴を使用
        messages = conversation_history.copy()

        # ユーザーメッセージを追加
        messages.append({"role": "user", "content": message})

        payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            LLM_API_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as res:
            res_body = res.read().decode("utf-8")
        res_json = json.loads(res_body)
        assistant_response = res_json["generated_text"]

        # アシスタントの応答を会話履歴に追加
        messages.append({"role": "assistant", "content": assistant_response})

        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
            },
            "body": json.dumps(
                {
                    "success": True,
                    "response": assistant_response,
                    "conversationHistory": messages,
                }
            ),
        }

    except Exception as error:
        print("Error:", str(error))

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
            },
            "body": json.dumps({"success": False, "error": str(error)}),
        }


if __name__ == "__main__":
    # テスト用イベントを作成
    sample_event = {
        "body": json.dumps({"message": "Hello, world!", "conversationHistory": []})
    }
    # contextは使用しないのでNoneを渡す
    response = lambda_handler(sample_event, None)
    # 結果を整形して出力
    print(json.dumps(response, indent=2, ensure_ascii=False))
