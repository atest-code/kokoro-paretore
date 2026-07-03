import streamlit as st
import requests
import random

# 設定
st.set_page_config(page_title="ココロの花木", layout="centered")
api_key = st.secrets.get("GEMINI_API_KEY")

# API通信関数（エラーを表示する設定）
def get_gemini_response(prompt, system_instruction):
    if not api_key:
        st.error("APIキーが見つかりません。")
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                           {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                           {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                           {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
    }
    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        if "candidates" in res_data:
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            st.error(f"APIレスポンスエラー: {res_data}")
            return None
    except Exception as e:
        st.error(f"通信例外: {e}")
        return None

# セッション状態の初期化
if "stage" not in st.session_state:
    st.session_state.update({"stage": "select_plant", "health": 50, "growth": "タネ・苗木", "plant_name": "", "plant_emoji": "🌱"})

# 画面制御
if st.session_state.stage == "select_plant":
    st.write("## 植物を選んでください")
    if st.button("🌵 サボテン"): 
        st.session_state.update({"plant_name": "サボテン", "plant_emoji": "🌵", "stage": "generate_event"})
        st.rerun()

elif st.session_state.stage == "generate_event":
    st.write("読み込み中...")
    raw = get_gemini_response(f"{st.session_state.plant_name}のピンチを作成", "フォーマット：【トラブル】〜 ●怒鳴る対応：〜 ●過保護対応：〜 ●ペアトレ対応：〜")
    if raw:
        # パース処理
        st.session_state.event_title = raw
        st.session_state.stage = "play"
        st.rerun()
    else:
        st.write("AIからの回答がありませんでした。")

elif st.session_state.stage == "play":
    st.write(st.session_state.event_title)
    if st.button("戻る"): st.session_state.stage = "select_plant"; st.rerun()