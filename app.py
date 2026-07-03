import streamlit as st
import requests
import random

# 画面設定
st.set_page_config(page_title="ココロの花木", page_icon="🌱", layout="centered", initial_sidebar_state="collapsed")
api_key = st.secrets.get("GEMINI_API_KEY")

# API通信関数（動作確認済みのモデル名を使用）
def get_gemini_response(prompt, system_instruction):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    try:
        response = requests.post(url, json=payload).json()
        if "candidates" in response:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        else:
            st.error(f"APIエラー: {response}")
            return None
    except Exception as e:
        st.error(f"接続エラー: {e}")
        return None

# 初期化
if "stage" not in st.session_state:
    st.session_state.update({"stage": "select_plant", "health": 50, "growth": "タネ・苗木", "plant_name": "", "plant_emoji": "🌱"})

st.markdown("<style>.block-container { max-width: 450px; } .stButton button { width: 100%; border-radius: 12px; padding: 14px; }</style>", unsafe_allow_html=True)

# 1. 選択
if st.session_state.stage == "select_plant":
    st.markdown("## 🌱 ココロの花木")
    if st.button("🌵 サボテン（こだわり派）"): st.session_state.update({"plant_name": "サボテン", "plant_emoji": "🌵", "stage": "generate_event"}); st.rerun()
    if st.button("🌻 ひまわり（衝動派）"): st.session_state.update({"plant_name": "ひまわり", "plant_emoji": "🌻", "stage": "generate_event"}); st.rerun()
    if st.button("🥀 ミモザ（HSC派）"): st.session_state.update({"plant_name": "ミモザ", "plant_emoji": "🥀", "stage": "generate_event"}); st.rerun()

# 2. 生成
elif st.session_state.stage == "generate_event":
    with st.spinner("思考中..."):
        sys_inst = "トラブルと対応3種を作成。フォーマット：【トラブル】〜 ●怒鳴る対応：〜 ●過保護対応：〜 ●ペアトレ対応：〜"
        raw = get_gemini_response(f"{st.session_state.plant_name}のピンチを作成", sys_inst)
        if raw:
            parts = raw.split("●")
            st.session_state.event_title = parts[0].replace("【トラブル】", "").strip()
            st.session_state.choices = []
            for p in parts[1:]:
                if "怒鳴る対応：" in p: st.session_state.choices.append({"type": "BAD", "text": p.replace("怒鳴る対応：", "").strip()})
                elif "過保護対応：" in p: st.session_state.choices.append({"type": "OVER", "text": p.replace("過保護対応：", "").strip()})
                elif "ペアトレ対応：" in p: st.session_state.choices.append({"type": "GOOD", "text": p.replace("ペアトレ対応：", "").strip()})
            st.session_state.stage = "play"
            st.rerun()

# 3. プレイ
elif st.session_state.stage == "play":
    st.markdown(f"### {st.session_state.plant_emoji} {st.session_state.plant_name}")
    st.write(f"成長段階: {st.session_state.growth} (元気度: {st.session_state.health})")
    st.progress(st.session_state.health / 100)
    st.info(st.session_state.event_title)
    for i, ch in enumerate(st.session_state.choices):
        if st.button(ch["text"], key=i):
            if ch["type"] == "GOOD":
                st.session_state.health = min(100, st.session_state.health + 20)
                st.session_state.growth = "👑 大輪の花" if st.session_state.health >= 85 else "🌱 すくすく成長中"
            elif ch["type"] == "BAD":
                st.session_state.health = max(10, st.session_state.health - 20)
                st.session_state.growth = "🌵 トゲトゲ・萎れ気味"
            else:
                st.session_state.health = max(10, st.session_state.health - 5)
                st.session_state.growth = "🌾 ひょろひょろ（栄養過多）"
            st.session_state.selected = ch
            st.session_state.stage = "result"
            st.rerun()

# 4. 結果
elif st.session_state.stage == "result":
    st.write(f"あなたの選択: {st.session_state.selected['text']}")
    advice = get_gemini_response(f"状況:{st.session_state.event_title} 対応:{st.session_state.selected['text']}", "この対応の解説を優しくして")
    st.info(advice)
    col1, col2 = st.columns(2)
    if col1.button("➡️ 次のピンチへ"): st.session_state.stage = "generate_event"; st.rerun()
    if col2.button("🔄 リセット"): st.session_state.stage = "select_plant"; st.rerun()