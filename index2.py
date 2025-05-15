import requests
from bs4 import BeautifulSoup
from langchain_aws import ChatBedrock
from langchain_community.callbacks.manager import get_bedrock_anthropic_callback

# -----------------------------
# Step 1: 試合データをスクレイピングしてテキスト整形
# -----------------------------

# 対象URL（日付を変えるときはここを編集）
url = "https://baseball.yahoo.co.jp/npb/schedule/?date=2025-05-13"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# チームリスト（12球団）
teams = ["巨人", "阪神", "中日", "広島", "ヤクルト", "DeNA",
         "ソフトバンク", "ロッテ", "楽天", "オリックス", "西武", "日本ハム"]

# HTMLからテキストノードをすべて抽出（空白除去済み）
all_text = list(soup.stripped_strings)

# スコア抽出（半角・全角・ハイフン対応）
results = []

for i in range(len(all_text) - 5):
    hyphen = all_text[i+2].strip()
    if (
        all_text[i] in teams and
        all_text[i+1].isdigit() and
        hyphen in ["-", "－", "–", "ー", "~"] and  # 表記ゆれ対応
        all_text[i+3].isdigit() and
        all_text[i+4] in teams
    ):
        team1 = all_text[i]
        score1 = all_text[i+1]
        score2 = all_text[i+3]
        team2 = all_text[i+4]
        results.append(f"{team1} {score1} - {score2} {team2}")

    elif (
        all_text[i] in teams and
        all_text[i+1] == "vs" and
        all_text[i+2] in teams and
        ("中止" in all_text[i+3] or "延期" in all_text[i+3])
    ):
        team1 = all_text[i]
        team2 = all_text[i+2]
        status = all_text[i+3]
        results.append(f"{team1} vs {team2}（{status}）")

# 結果が抽出できていない場合はエラー表示して終了
if not results:
    print("⚠ 試合結果の抽出に失敗しました。HTML構造が変わっている可能性があります。")
    print("🔍 soup.stripped_strings を出力して調査してください。")
    exit()

# 構造化済み試合結果を整形
game_text = "\n".join(results)

# -----------------------------
# Step 2: Claude（Bedrock）で勝敗判定
# -----------------------------

llm = ChatBedrock(
    credentials_profile_name="Bedrock-fullaccess",
    region_name="ap-northeast-1",
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    model_kwargs={
        "max_tokens": 1000,
        "temperature": 0.1
    },
)

with get_bedrock_anthropic_callback() as callback:

    question = f"""
以下は、2025年5月13日に行われた日本のプロ野球の試合結果です：

{game_text}

この情報を基に、出場チームごとに勝敗を判定し、以下のJSON形式で出力してください：

出力形式：
{{
  "team_name": "チーム名",
  "won": true
}}

【出力規則】
- 引き分け、中止、スコア不明の場合は "won": false にしてください
- 出場しているすべてのチームを対象に出力してください
- チーム名は以下の一覧と一致するように正確に記載してください：

【対象チーム】
・巨人 ・阪神 ・DeNA ・広島 ・ヤクルト ・中日
・ソフトバンク ・日本ハム ・ロッテ ・楽天 ・オリックス ・西武
"""

    print('\n 質問: ', question)

    # これで質問を投げます
    result = llm.invoke(question)

    # 「AIMessage」という形で返されるため、見やすくするために content 項目を print します。
    # https://api.python.langchain.com/en/latest/messages/langchain_core.messages.ai.AIMessage.html
    print('\n 回答: ', result.content)

    # 最後に、消費したトークン数と費用を出力します。
    print('\n レポート:', callback)