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
        "temperature": 0.9
    },
)

# Yahoo!プロ野球の試合結果ページからHTMLを取得
url = "https://baseball.yahoo.co.jp/npb/schedule/?date=2025-04-14"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# bodyタグの中身だけ取り出す（ノイズ軽減目的）
html = soup.body.prettify()

# LLMへの問い合わせ（htmlをquestionに埋め込む！）
with get_bedrock_anthropic_callback() as callback:

    question = f"""
以下のHTMLは、日本のプロ野球の試合結果が記載されたHTMLです。
このHTMLには各試合のスコア、チーム名が含まれています。

HTML：
{html}

HTMLを読み取り、2025年4月14日の出場チームごとに勝敗を判定し、以下のJSON形式で出力してください：

出力形式：
{{
  "team_name": "チーム名",
  "won": true
}}

【出力規則】
- 出力対象の日付は2025年4月14日です。
- step-by-stepで処理してください。まずは、対象日に試合があったかどうかを判定してください。試合がなかった場合には、すべて"won": falseとしてください。
- 試合があった場合には、出場しているすべてのチームについて出力してください
- 指定のJSONフォーマットで出力してください
- 引き分け・中止の場合は "won": false にしてください
- HTMLには他の日付の試合結果も含まれている可能性があります。他の日の試合結果がHTML中に記載されていても、**それらは絶対に無視して、必ず当該日付に対応する情報のみを対象にしてください。**


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

"""

    print('\n 質問: ', question)

    # これで質問を投げます
    result = llm.invoke(question)

    # 「AIMessage」という形で返されるため、見やすくするために content 項目を print します。
    # https://api.python.langchain.com/en/latest/messages/langchain_core.messages.ai.AIMessage.html
    print('\n 回答: ', result.content)

    # 最後に、消費したトークン数と費用を出力します。
    print('\n レポート:', callback)