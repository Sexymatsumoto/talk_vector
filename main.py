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

これから与える本文は、営業担当者が実際に行ったトーク内容です。  
本文は十分な情報を含んでいると仮定し、追加で質問をすることなく、  
与えられた情報だけをもとに分析と評価を行ってください。

【評価指示】
次の7つの観点ごとに、
- ◎（非常に良い）／○（普通に良い）／△（改善の余地あり）
で評価してください。

また、各観点ごとに必ず
- 本文中から具体的なフレーズや表現を引用して、どこを根拠に評価したか説明してください。

もし該当するフレーズが本文に見当たらない場合は、
- 「本文には明確な該当表現がなかったが、〇〇というニュアンスから判断した」と記載してください。

【7つの観点】
- お客様の「欲しい！」気持ちを引き出しているか？
- 商品・サービスの内容が直感的にわかりやすいか？
- 将来の展開イメージが持てるか？
- 他社との違い（競争優位性）が伝わっているか？
- 価格に納得感があるか？
- 今すぐ行動したくなるメリットが伝わっているか？
- 行動を止める不安を減らすメッセージがあるか？

さらに、まとめとして
- 総合評価（◎／○／△）
- 総合評価の理由（100字以内）
- 総合評価に基づく具体的な改善アドバイス（150字以内＋できればサンプルトーク例を添える）

【出力形式】
出力形式は**HTMLテーブル**で、次のようにしてください。

【HTML出力例】
<table border="1" style="border-collapse:collapse;">
<tr><th>観点</th><th>評価</th><th>根拠</th></tr>
<tr><td>お客様の「欲しい！」気持ちを引き出しているか？</td><td>◎</td><td>「この美しさと薄さで映画館のような迫力体験を」などの表現が購買意欲を刺激しているため。</td></tr>
<tr><td>商品・サービスの内容が直感的にわかりやすいか？</td><td>○</td><td>商品の機能説明はされているが、やや情報過多で整理されていないため。</td></tr>
<tr><td>将来の展開イメージが持てるか？</td><td>△</td><td>利用シーンは想起できるが、未来像の具体例が少ないため。</td></tr>
<tr><td>他社との違い（競争優位性）が伝わっているか？</td><td>○</td><td>「液晶テレビのパイオニア」という訴求で差別化が図られているため。</td></tr>
<tr><td>価格に納得感があるか？</td><td>◎</td><td>値引きの説明はあるが、コストパフォーマンス訴求が弱いため。</td></tr>
<tr><td>今すぐ行動したくなるメリットが伝わっているか？</td><td>○</td><td>「期間限定特典」などの要素はあるが、緊急性の演出が弱い。</td></tr>
<tr><td>行動を止める不安を減らすメッセージがあるか？</td><td>△</td><td>購入後のサポートや保証についての言及が不足しているため。</td></tr>
<tr><td>総合評価</td><td colspan="2">○</td></tr>
<tr><td>総合評価の理由</td><td colspan="2">商品内容は明確だが、将来展開の具体性が不足している。</td></tr>
<tr><td>改善アドバイス</td><td colspan="2">購入後のサポート体制や成功事例を示すトークを加えましょう。<br>例：「この商品はご購入後も3年間無料保証がついておりますので、安心してご利用いただけます。」</td></tr>
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
