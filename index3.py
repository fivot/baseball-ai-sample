from langchain_aws import ChatBedrock
from langchain_community.callbacks.manager import get_bedrock_anthropic_callback
import requests
from bs4 import BeautifulSoup

# llm: LLM (Large Language Models) 、つまり、「大規模言語モデル」を指します。
# langchain_aws から提供されている ChatBedrock を利用します。
llm = ChatBedrock(
credentials_profile_name="Bedrock-fullaccess",
    # Bedrock を利用するリージョンを指定します
    region_name="ap-northeast-1",

    # モデルIDの一覧はこちらで確認することができます。
    # https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html#model-ids-arns
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",

    # LLM に与えるパラメータ情報をセットします。指定できる項目や最小値・最大値など詳細については、以下のリンクで確認できます。
    # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html#model-parameters-anthropic-claude-messages-request-response
    model_kwargs={
        # 利用する最大トークン数を指定します。
        "max_tokens": 1000,
        # 回答のランダム性を指定します。最小値は0, 最大値は1です。値が大きいほど多様な回答が返されます。
        "temperature": 0.1
    },
)
# HTMLを取得
url = "https://baseball.yahoo.co.jp/npb/schedule/?date=2025-05-13"
html = BeautifulSoup(requests.get(url).text, "html.parser").body.prettify()

# LLMへの問い合わせ
with get_bedrock_anthropic_callback() as callback:
    question = f"""
以下は、プロ野球の試合結果を取得するためのテンプレートです。

--- formatJSON ---
https://baseball.yahoo.co.jp/npb/schedule/?date={{.date}}

このページから{{.date}}の各球団の試合結果を、以下のjsonフォーマットで返してください。

{{
"team_name": string,
"result": boolean
}}

ex)
{{
"team_name": "楽天",
"result": true
}}

--- formatTextAllTeam ---
{{.date}}の各球団の試合結果を返してください。

【出力規則】
- 指定のJSONフォーマットで出力してください
- 試合が行われなかった、引き分けの場合は「won」をfalseにしてください
- すべてのチームについて、必ず結果を出力してください

【対象チーム】
・巨人
・阪神
・DeNA
・広島
・ヤクルト
・中日
・ソフトバンク
・日本ハム
・ロッテ
・楽天
・オリックス
・西武

--- formatTextOneTeam ---
https://baseball.yahoo.co.jp/npb/schedule/?date={{.date}}

このページから{{.team_name}}の試合結果を返してください。

【出力規則】
- 指定のJSONフォーマットで出力してください
- 試合が行われなかった、引き分けの場合は「won」をfalseにしてください

--- formatTextAllTeamForHTML ---
以下のHTML要素から各球団の試合結果を返してください。

{{.html}}

【出力規則】
- 指定のJSONフォーマットで出力してください
- 試合が行われなかった、引き分けの場合は「won」をfalseにしてください
- すべてのチームについて、必ず結果を出力してください

【対象チーム】
・巨人
・阪神
・DeNA
・広島
・ヤクルト
・中日
・ソフトバンク
・日本ハム
・ロッテ
・楽天
・オリックス
・西武

--- formatTextOneTeamForHTML ---
以下のHTML要素から{{.team_name}}の試合結果を返してください。

{{.html}}

【出力規則】
- 指定のJSONフォーマットで出力してください
- 試合が行われなかった、引き分けの場合は「won」をfalseにしてください

"""


    print('\n 質問: ', question)

    # これで質問を投げます
    result = llm.invoke(question)

    # 「AIMessage」という形で返されるため、見やすくするために content 項目を print します。
    # https://api.python.langchain.com/en/latest/messages/langchain_core.messages.ai.AIMessage.html
    print('\n 回答: ', result.content)

    # 最後に、消費したトークン数と費用を出力します。
    print('\n レポート:', callback) 