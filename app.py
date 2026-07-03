import streamlit as st
import requests
import random

# 1. スマホ風の画面サイズに設定
st.set_page_config(
    page_title="ココロの花木", 
    page_icon="🌱", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# APIキーの取得
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーがSecretsに設定されていません。")
    st.stop()

# 直接通信用の関数
def call_gemini(prompt, system_instruction):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        st.error(f"APIエラー: {response.text}")
        return ""
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# セッション状態の初期化
if "stage" not in st.session_state:
    st.session_state.stage = "select_plant"
    st.session_state.plant_name = ""
    st.session_state.plant_emoji = "🌱"
    st.session_state.health = 50
    st.session_state.growth = "タネ・苗木"

# CSSデザイン
st.markdown("""
    <style>
    .block-container { max-width: 450px; padding-top: 2rem; }
    .stButton button { width: 100%; border-radius: 12px; padding: 14px; font-size: 15px; }
    .plant-box { text-align: center; background-color: #f0f7f4; padding: 20px; border-radius: 20px; margin-bottom: 15px; border: 1px solid #e0ebd3; }
    </style>
""", unsafe_allow_html=True)

# --- 画面1: 植物選択 ---
if st.session_state.stage == "select_plant":
    st.markdown("## 🌱 ココロの花木")
    if st.button("🌵 サボテン（こだわり派）"):
        st.session_state.plant_name = "サボテン"; st.session_state.plant_emoji = "🌵"; st.session_state.stage = "generate_event"; st.rerun()
    if st.button("🌻 ひまわり（衝動派）"):
        st.session_state.plant_name = "ひまわり"; st.session_state.plant_emoji = "🌻"; st.session_state.stage = "generate_event"; st.rerun()
    if st.button("🥀 ミモザ（HSC派）"):
        st.session_state.plant_name = "ミモザ"; st.session_state.plant_emoji = "🥀"; st.session_state.stage = "generate_event"; st.rerun()

# --- 画面2: イベント生成 ---
elif st.session_state.stage == "generate_event":
    with st.spinner("AIがピンチを生成中..."):
        sys_inst = "あなたはペアトレコーチです。特性に合わせたトラブルと対応3種（怒鳴る、過保護、ペアトレ）を生成。フォーマット：【トラブル】〜 ●怒鳴る対応：〜 ●過保護対応：〜 ●ペアトレ対応：〜"
        raw = call_gemini(f"{st.session_state.plant_name}が起こしそうなトラブルを考えて", sys_inst)
        
        parts = raw.split("●")
        st.session_state.event_title = parts[0].replace("【トラブル】", "").strip()
        choices = []
        for p in parts[1:]:
            if "怒鳴る対応：" in p: choices.append({"type": "BAD", "text": p.replace("怒鳴る対応：", "").strip()})
            elif "過保護対応：" in p: choices.append({"type": "OVER", "text": p.replace("過保護対応：", "").strip()})
            elif "ペアトレ対応：" in p: choices.append({"type": "GOOD", "text": p.replace("ペアトレ対応：", "").strip()})
        
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.stage = "play"
        st.rerun()

# --- 画面3: ゲーム画面 ---
elif st.session_state.stage == "play":
    st.info(st.session_state.event_title)
    for i, ch in enumerate(st.session_state.shuffled_choices):
        if st.button(ch["text"], key=i):
            st.session_state.selected = ch
            st.session_state.stage = "result"
            st.rerun()

# --- 画面4: 結果画面 ---
elif st.session_state.stage == "result":
    st.write(f"あなたが選んだ対応: {st.session_state.selected['text']}")
    
    with st.spinner("コーチが解説中..."):
        prompt = f"トラブル: {st.session_state.event_title}。選んだ対応: {st.session_state.selected['text']}"
        advice = call_gemini(prompt, "なぜその対応がどうなったか、親に共感しつつ解説して")
        st.info(advice)
        
    if st.button("➡️ 次のピンチへ / 🔄 リセット"):
        st.session_state.stage = "select_plant"
        st.rerun()