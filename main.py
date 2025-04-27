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
def call_gpt_raw_log(query, full_text):
    prompt = f"""
あなたは営業トークのコンサルタントです。

以下は、ある営業トークの全文です。

【本文】
{full_text}

この営業トークについて、次の7つの観点から多面的に評価してください。

- お客様の「欲しい！」気持ちを引き出しているか？
- 商品・サービスの内容が直感的にわかりやすいか？
- 将来の展開イメージが持てるか？
- 他社との違い（競争優位性）が伝わっているか？
- 価格に納得感があるか？
- 今すぐ行動したくなるメリットが伝わっているか？
- 行動を止める不安を減らすメッセージがあるか？

以下の形式で出力してください。

1. 総合評価（◎／○／△）＋簡単な理由（100字以内）

2. 特に補強すべきポイント（簡単に）

3. 伸ばすべき強み（簡単に）

※ コードブロックの書き出しに ```plaintext や ```text などの指定は不要です。
※ 出力はすべて日本語でお願いします。
※ 改行は2回以上しないこと。
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
        if raw_queries:
            queries = [q.strip() for q in raw_queries.split("\n") if q.strip()]
        else:
            queries = ["営業トーク全体"]

        results = []

        for query in queries:
            gpt_output = call_gpt_raw_log(query, full_text)
            
            try:
                # 各項目ごとに行頭を探して分割
                evaluation = ""
                weak_point = ""
                strong_point = ""

                lines = gpt_output.splitlines()
                for line in lines:
                    if line.startswith("1."):
                        evaluation = line[2:].strip()
                    elif line.startswith("2."):
                        weak_point = line[2:].strip()
                    elif line.startswith("3."):
                        strong_point = line[2:].strip()

                results.append({
                    "クエリ": query,
                    "評価（◎○△＋理由）": evaluation,
                    "特に補強すべきポイント": weak_point,
                    "伸ばすべき強み": strong_point
                })

            except Exception as e:
                results.append({
                    "クエリ": query,
                    "評価（◎○△＋理由）": "エラー",
                    "特に補強すべきポイント": "エラー",
                    "伸ばすべき強み": "エラー"
                })

        # forの外でデータフレーム作成・表示
        df = pd.DataFrame(results)
        st.success("✅ 出力完了！")
        st.dataframe(df)

        # CSV出力
        st.download_button(
            label="📥 クエリ×GPT出力CSVをダウンロード",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="gpt_query_outputs.csv",
            mime="text/csv"
        )
