import streamlit as st
import requests
import random

# --- 設定 ---
st.set_page_config(page_title="ココロの花木", page_icon="🌱", layout="centered", initial_sidebar_state="collapsed")
api_key = st.secrets.get("GEMINI_API_KEY")

# API直接通信関数
def get_gemini_response(prompt, system_instruction):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        st.error(f"エラー発生: {e}")
        return None

# セッション状態の初期化
if "stage" not in st.session_state:
    st.session_state.update({
        "stage": "select_plant", "health": 50, "growth": "タネ・苗木", 
        "plant_name": "", "plant_emoji": "🌱", "event_title": "", "shuffled_choices": []
    })

# CSS
st.markdown("""<style>
    .block-container { max-width: 450px; }
    .stButton button { width: 100%; border-radius: 12px; padding: 14px; }
    .plant-box { text-align: center; background-color: #f0f7f4; padding: 20px; border-radius: 20px; margin-bottom: 15px; }
</style>""", unsafe_allow_html=True)

# --- 画面制御 ---
if st.session_state.stage == "select_plant":
    st.markdown("## 🌱 ココロの花木")
    if st.button("🌵 サボテン（こだわり派）"): st.session_state.update({"plant_name": "サボテン", "plant_emoji": "🌵", "stage": "generate_event"}); st.rerun()
    if st.button("🌻 ひまわり（衝動派）"): st.session_state.update({"plant_name": "ひまわり", "plant_emoji": "🌻", "stage": "generate_event"}); st.rerun()
    if st.button("🥀 ミモザ（HSC派）"): st.session_state.update({"plant_name": "ミモザ", "plant_emoji": "🥀", "stage": "generate_event"}); st.rerun()

elif st.session_state.stage == "generate_event":
    with st.spinner("ピンチを生成中..."):
        sys_inst = "トラブルと対応3種を作成。フォーマット：【トラブル】〜 ●怒鳴る対応：〜 ●過保護対応：〜 ●ペアトレ対応：〜"
        raw = get_gemini_response(f"{st.session_state.plant_name}が起こすトラブルを作成して", sys_inst)
        if raw:
            parts = raw.split("●")
            st.session_state.event_title = parts[0].replace("【トラブル】", "").strip()
            st.session_state.shuffled_choices = [
                {"type": "BAD", "text": p.replace("怒鳴る対応：", "").strip()} if "怒鳴る対応：" in p else
                {"type": "OVER", "text": p.replace("過保護対応：", "").strip()} if "過保護対応：" in p else
                {"type": "GOOD", "text": p.replace("ペアトレ対応：", "").strip()} for p in parts[1:]
            ]
            random.shuffle(st.session_state.shuffled_choices)
            st.session_state.stage = "play"
            st.rerun()

elif st.session_state.stage == "play":
    st.markdown(f"<div class='plant-box'><h3>{st.session_state.plant_name}</h3><p>状態: {st.session_state.growth}</p></div>", unsafe_allow_html=True)
    st.progress(st.session_state.health / 100)
    st.info(st.session_state.event_title)
    for i, ch in enumerate(st.session_state.shuffled_choices):
        if st.button(ch["text"], key=i):
            st.session_state.selected = ch
            # ステータス変動
            if ch["type"] == "GOOD": st.session_state.health += 20; st.session_state.growth = "すくすく成長中"
            elif ch["type"] == "BAD": st.session_state.health -= 20; st.session_state.growth = "トゲトゲ・萎れ気味"
            else: st.session_state.health -= 5; st.session_state.growth = "ひょろひょろ"
            st.session_state.health = max(10, min(100, st.session_state.health))
            st.session_state.stage = "result"
            st.rerun()

elif st.session_state.stage == "result":
    st.write(f"あなたが選んだ対応: {st.session_state.selected['text']}")
    advice = get_gemini_response(f"状況:{st.session_state.event_title} 対応:{st.session_state.selected['text']}", "この対応の解説を優しくして")
    st.info(advice)
    col1, col2 = st.columns(2)
    if col1.button("➡️ 次のピンチへ"): st.session_state.stage = "generate_event"; st.rerun()
    if col2.button("🔄 別の植物へ"): st.session_state.stage = "select_plant"; st.rerun()