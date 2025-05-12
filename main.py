import streamlit as st
import openai
import time

# OpenAI APIキー
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AIトーク分析ツール", layout="centered")
st.title("🧠 AIトーク分析ツール")

# -------------------------
# 1. 用途選択
# -------------------------
mode = st.selectbox("🎯 分析用途を選んでください", ["営業トーク分析", "採用メッセージ分析"])

# -------------------------
# 2. トーク本文入力
# -------------------------
full_text = st.text_area("🎤 分析したい本文を入力してください", height=300)

# -------------------------
# 3. クエリ（評価観点）入力
# -------------------------
default_sales_queries = """【7つの観点】
- お客様の「欲しい！」気持ちを引き出しているか？
- 商品・サービスの内容が直感的にわかりやすいか？
- 将来の展開イメージが持てるか？
- 他社との違い（競争優位性）が伝わっているか？
- 価格に納得感があるか？
- 今すぐ行動したくなるメリットが伝わっているか？
- 行動を止める不安を減らすメッセージがあるか？
"""

default_recruit_queries = """【7つの観点】
- 組織の雰囲気や文化が伝わっているか？
- 仕事内容や役割がイメージしやすいか？
- 他社との違いや独自性が明確か？
- 成長やキャリアの可能性が示されているか？
- 応募者にとってのメリットが伝わっているか？
- 不安やリスクに対する配慮があるか？
- 応募を後押しする呼びかけがあるか？
"""

raw_queries = st.text_area(
    "🔍 評価観点を1行ずつ入力してください（空欄でもOK）",
    value=default_sales_queries if mode == "営業トーク分析" else default_recruit_queries,
    height=250
)

# -------------------------
# 4. GPTコール関数
# -------------------------
def generate_prompt(text, queries, mode):
    if mode == "営業トーク分析":
        role = "営業トークのコンサルタント"
        subject = "営業担当者が実際に行ったトーク内容"
    else:
        role = "採用ブランディングの専門家"
        subject = "ある会社が求職者向けに発信した採用メッセージ"

    return f"""
あなたは{role}です。

これから与える本文は、{subject}です。
本文は十分な情報を含んでいると仮定し、追加で質問をすることなく、
与えられた情報だけをもとに分析と評価を行ってください。

【評価指示】
次の観点ごとに、
- ◎（非常に良い）／○（普通に良い）／△（改善の余地あり）で評価してください。

また、各観点ごとに必ず
- 本文中から具体的なフレーズや表現を引用して、どこを根拠に評価したか説明してください。
該当が見つからない場合は、「本文には明確な該当表現がなかったが、〇〇というニュアンスから判断した」と記載してください。

{queries}

最後に以下を出力してください：
- 総合評価（◎／○／△）
- 総合評価の理由（100字以内）
- 改善アドバイス（150字以内＋例文があれば添える）

出力形式はHTMLテーブルでお願いします。
※出力のHTMLタグはすべてエスケープせずに、そのままの形式で出力してください。
"""

def call_gpt(text, queries, mode):
    prompt = generate_prompt(text, queries, mode)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt + f"\n\n【本文】\n{text}"}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"エラーが発生しました: {e}"

# -------------------------
# 5. 実行ボタン
# -------------------------
if st.button("▶ AI分析スタート") and full_text:
    with st.spinner("AIが分析中です..."):
        time.sleep(2)
        result = call_gpt(full_text, raw_queries, mode)
    st.success("✅ 分析完了！")
    st.markdown(result, unsafe_allow_html=True)
