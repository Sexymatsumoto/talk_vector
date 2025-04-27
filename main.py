import streamlit as st
import pandas as pd
import openai

# OpenAI APIキー
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="トークベクトル分析ツール", layout="centered")
st.title("📝 トークベクトル分析ツール")

# トーク本文入力
full_text = st.text_area("🎤 あなたの営業トークを入力してください（コピペOK）", height=300)

# クエリ入力（今回はもう固定でもOKだけど一応残す）
raw_queries = st.text_area("🔍 クエリを1行ずつ入力してください（空欄でもOK）", height=200)

# GPTプロンプト（全文評価系）
def call_gpt_raw_log(full_text):
    prompt = f"""
あなたは営業トークのコンサルタントです。

以下の営業トークについて、次の7つの観点でそれぞれ ◎（非常に良い）／○（普通に良い）／△（改善の余地あり）で評価してください。

- お客様の「欲しい！」気持ちを引き出しているか？
- 商品・サービスの内容が直感的にわかりやすいか？
- 将来の展開イメージが持てるか？
- 他社との違い（競争優位性）が伝わっているか？
- 価格に納得感があるか？
- 今すぐ行動したくなるメリットが伝わっているか？
- 行動を止める不安を減らすメッセージがあるか？

さらに総合評価（◎／○／△）と簡単な理由（100字以内）も記載してください。

出力形式は**HTMLテーブル**で、次のようにしてください。

【HTML出力例】
<table border="1" style="border-collapse:collapse;">
<tr><th>観点</th><th>評価</th></tr>
<tr><td>欲しい気持ち引き出し</td><td>◎</td></tr>
<tr><td>内容わかりやすさ</td><td>○</td></tr>
<tr><td>将来イメージ</td><td>△</td></tr>
<tr><td>競争優位性</td><td>○</td></tr>
<tr><td>価格納得感</td><td>◎</td></tr>
<tr><td>行動メリット</td><td>○</td></tr>
<tr><td>不安解消</td><td>△</td></tr>
<tr><td>総合評価</td><td>○（理由：情熱的だが情報整理に課題あり）</td></tr>
</table>

※ コードブロックの書き出し（```htmlなど）は不要です。
※ 出力はすべて日本語でお願いします。
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"エラー: {e}"

# 実行処理
if st.button("▶ GPT出力スタート") and full_text:
    with st.spinner("GPT処理中..."):
        gpt_output = call_gpt_raw_log(full_text)
        st.success("✅ 出力完了！")

        # ここでHTMLとして表示！！
        st.markdown(gpt_output, unsafe_allow_html=True)
