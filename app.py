import os
import random
import streamlit as st
import google.generativeai as genai

# 1. スマホ風の画面サイズに設定
st.set_page_config(
    page_title="ココロの花木", 
    page_icon="🌱", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🚨 新キー（AQ.形式）のNotFoundエラーを強制回避するベータ版ルーティング設定
if "GEMINI_API_KEY" in st.secrets:
    # 👈 環境変数に直接ベータ版を指定することで、ライブラリのバグを安全に回避します
    os.environ["CONF_API_VERSION"] = "v1beta"
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーがSecretsに設定されていません。")

# セッション状態の初期化
if "stage" not in st.session_state:
    st.session_state.stage = "select_plant"
    st.session_state.plant_name = ""
    st.session_state.plant_emoji = "🌱"
    st.session_state.health = 50  # 植物の元気度
    st.session_state.growth = "タネ・苗木"
    st.session_state.event_title = ""
    st.session_state.shuffled_choices = [] # シャッフルされた選択肢のリスト

# スマホ風のデザイン調整（CSS）
st.markdown("""
    <style>
    .block-container { max-width: 450px; padding-top: 2rem; }
    .stButton button { width: 100%; border-radius: 12px; padding: 14px; font-size: 15px; white-space: normal; text-align: left; line-height: 1.4; }
    .plant-box { text-align: center; background-color: #f0f7f4; padding: 20px; border-radius: 20px; margin-bottom: 15px; border: 1px solid #e0ebd3; }
    .custom-sub { color: #555; font-size: 14px; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 画面1: キャラクター（花木）選択 ---
if st.session_state.stage == "select_plant":
    st.markdown("<h2 style='text-align: center; color: #2e6f40;'>🌱 ココロの花木</h2>", unsafe_allow_html=True)
    st.markdown("<p class='custom-sub'>あなたのお子さんはどのタイプ？<br>特性を植物に例えてペアトレを学びます</p>", unsafe_allow_html=True)
    
    if st.button("🌵 サボテン (マイペース・触るとトゲがある)\n【こだわり派・過干渉を嫌う・自分の世界を持つ子】"):
        st.session_state.plant_name = "サボテン（こだわり派・過干渉が苦手）"
        st.session_state.plant_emoji = "🌵"
        st.session_state.stage = "generate_event"
        st.rerun()
        
    if st.button("🌻 ひまわり (元気いっぱい・注意が散る)\n【衝動的・エネルギー全開・集中が続きにくい子】"):
        st.session_state.plant_name = "ひまわり（衝動的・エネルギー全開）"
        st.session_state.plant_emoji = "🌻"
        st.session_state.stage = "generate_event"
        st.rerun()
        
    if st.button("🥀 ミモザ (刺激に敏感・すぐ閉じちゃう)\n【HSC傾向・環境に敏感で傷つきやすいデリケートな子】"):
        st.session_state.plant_name = "ミモザ（HSC・とてもデリケート）"
        st.session_state.plant_emoji = "🥀"
        st.session_state.stage = "generate_event"
        st.rerun()

# --- 画面2: AIによるピンチイベント＆高難易度選択肢の生成 ---
elif st.session_state.stage == "generate_event":
    with st.spinner("日常のピンチを読み込み中..."):
        
        situations = [
            "朝の登校・登園準備（時間がないのに動かない、着替えない、別のことを始めるなど）",
            "夕方の帰宅後から夕食まで（宿題を始めない、手洗いを嫌がる、ずっと動画やゲームを辞めないなど）",
            "夜のお風呂や寝る前の時間（お風呂に入りたがらない、布団に入ってもいつまでもテンションが高いなど）",
            "休日のお出かけ先やお店の中（急な予定変更で不機嫌、お店のものを触りまくる、些細なことでパニックなど）",
            "片付けやルール変更（おもちゃを散らかしっぱなし、片付けを指示しても無視する、ゲームの制限時間が来て暴れるなど）",
            "食事中のトラブル（途中で立ち歩く、好き嫌いが激しくて食べない、クチャクチャ食べるなど）"
        ]
        chosen_situation = random.choice(situations)
        
        plant_profiles = (
            "【🌵 サボテン（ASD傾向 / こだわり派）の特性】\n"
            "- 特徴: 自分の世界やルールを強く持ち、急な予定変更や『～しなさい』という命令（過干渉）が大の苦手。触るとトゲで反発する。\n"
            "- 罠対応（BAD/OVER）: 『なんで言う通りにできないの！』とお説教する（BAD）、または機嫌を損ねないよう親が先回りしてお膳立てする（OVER）。\n"
            "- ペアトレ流（GOOD）: 見通しを伝える（予告）、視覚化、選択肢を提示して『自分で選んだ』と思わせる。命令ではなく『〇〇したら教えてね』と境界線を作る。\n\n"
            "【🌻 ひまわり（ADHD傾向 / 衝動・多動派）の特性】\n"
            "- 特徴: 元気いっぱいで悪気はないが、ワーキングメモリが小さく、刺激にすぐ気を取られて集中が続かない。指示をすぐに忘れる。\n"
            "- 罠対応（BAD/OVER）: 『前にも言ったでしょ！』と長々とお説教する（長い話は脳から消えるためBAD）、または動かないからと親が全部代わりにやってあげる（OVER）。\n"
            "- ペアトレ流（GOOD）: 刺激を減らす環境調整、1回に1つの短い指示（ワンステップ）、行動のハードルを極限まで下げる、できた瞬間に即ほめる（CCQ: 穏やかに、近づいて、静かに）。\n\n"
            "【🥀 ミモザ（HSC / 刺激に敏感派）の特性】\n"
            "- 特徴: 感受性が非常に豊かで、他人の表情や場の空気、音や光などの刺激を過剰にキャッチして疲れやすい。傷つきやすく、不安から貝のように心を閉じる。\n"
            "- 罠対応（BAD/OVER）: 『これくらいで泣かないの！』としつける（BAD）、または可哀想だからと親が一緒になって過剰にオロオロと共感しすぎる（親の不安が伝染してパニックが長引くOVER）。\n"
            "- ペアトレ流（GOOD）: まず親が落ち着く（感情のアンカー）、静かで安全な場所の確保（クールダウン）、不安を煽らず『大丈夫、ここにいるよ』と短い言葉で見守り、淡々と次の行動へ促す。"
        )
        
        system_instruction = (
            "あなたは発達障害・凸凹児のペアレントトレーニングを植物育成ゲームに例えて教える超一流のコーチです。\n\n"
            f"以下の特性プロファイルを深く理解してください：\n{plant_profiles}\n\n"
            f"現在選択されている植物タイプ【{st.session_state.plant_name}】の子どもが、"
            f"指定されたシチュエーション【{chosen_situation}】で起こしそうな、この特性特有のリアルな困りごとを1つ提示し、親の対応選択肢を3つ作ってください。\n\n"
            "【重要：選択肢の難易度設定】\n"
            "育児書や世間一般では『丁寧で正しいしつけ』『優しい神対応』と思われがちですが、実はその特性の子ども（ADHD/ASD/HSC）には逆効果やパニック悪化になってしまう『もったいない罠対応』を必ず混ぜてください。親御さんがリアルに『え、これがダメなの！？』と本気で迷う選択肢にしてください。\n\n"
            "●怒鳴る・お説教対応（BAD）：\n"
            "単なる怒鳴り声ではなく、『世間一般の正論や、良かれと思って優しく長々と言い聞かせるお説教・しつけ』にしてください。\n"
            "●過保護・ご褒美対応（OVER）：\n"
            "『親が先回りして失敗を防ぐ、ご褒美や物で釣る、または良かれと思って過剰に共感・同調して寄り添いすぎる対応』にしてください。\n"
            "●ペアトレ対応（GOOD）：\n"
            "上記のプロファイルに基づいた『その特性にベストな環境調整、ワンステップでの具体的・肯定的な指示、あえて静かに見守る対応』にしてください。\n\n"
            "フォーマットは必ず以下を厳守し、選択肢のテキスト自体にGOODやBADといった正解を匂わせる言葉は絶対に入れないでください：\n"
            "【トラブル】\n（具体的な状況説明）\n"
            "●怒鳴る対応：\n（親のセリフや行動の記述）\n"
            "●過保護対応：\n（親のセリフや行動の記述）\n"
            "●ペアトレ対応：\n（親のセリフや行動の記述）"
        )
        
        # models/ 指定のまま維持
        model = genai.GenerativeModel(
            model_name='models/gemini-1.5-flash',
            system_instruction=system_instruction
        )
        response = model.generate_content(
            f"【{st.session_state.plant_name}】が【{chosen_situation}】で起こすリアルなトラブルと、罠を含んだ3つの対応方法を作ってください。"
        )
        
        raw_text = response.text
        parts = raw_text.split("●")
        st.session_state.event_title = parts[0].replace("【トラブル】", "").strip()
        
        choices = []
        for part in parts[1:]:
            if "怒鳴る対応：" in part:
                choices.append({"type": "BAD", "text": part.replace("怒鳴る対応：", "").strip()})
            elif "過保護対応：" in part:
                choices.append({"type": "OVER", "text": part.replace("過保護対応：", "").strip()})
            elif "ペアトレ対応：" in part:
                choices.append({"type": "GOOD", "text": part.replace("ペアトレ対応：", "").strip()})
        
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        
        st.session_state.stage = "play"
        st.rerun()

# --- 画面3: メインゲーム画面 ---
elif st.session_state.stage == "play":
    st.markdown(f"""
    <div class='plant-box'>
        <span style='font-size: 80px;'>{st.session_state.plant_emoji}</span>
        <h3>{st.session_state.plant_name}</h3>
        <p>状態: <b>{st.session_state.growth}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"水分・元気度: {st.session_state.health} / 100")
    st.progress(st.session_state.health / 100)
    st.write("---")
    
    st.markdown("### 🚨 日常のピンチ！")
    st.info(st.session_state.event_title)
    st.write("---")
    st.markdown("🗣️ **あなたならどう声をかける？**")
    
    for i, choice in enumerate(st.session_state.shuffled_choices):
        if st.button(choice["text"], key=f"choice_{i}"):
            st.session_state.selected_type = choice["type"]
            st.session_state.selected_text = choice["text"]
            
            if choice["type"] == "GOOD":
                st.session_state.health = min(100, st.session_state.health + 20)
                if st.session_state.health >= 85:
                    st.session_state.growth = "👑 大輪の花（見事な成長！）"
                else:
                    st.session_state.growth = "🌱 すくすく成長中"
            elif choice["type"] == "BAD":
                st.session_state.health = max(10, st.session_state.health - 20)
                st.session_state.growth = "🌵 トゲトゲ・萎れ気味"
            else: # OVER
                st.session_state.health = max(10, st.session_state.health - 5)
                st.session_state.growth = "🌾 ひょろひょろ（栄養過多）"
                
            st.session_state.stage = "result"
            st.rerun()

# --- 画面4: 結果・フィードバック ---
elif st.session_state.stage == "result":
    st.markdown(f"<div style='text-align:center; font-size:50px;'>{st.session_state.plant_emoji}</div>", unsafe_allow_html=True)
    st.progress(st.session_state.health / 100)
    
    if st.session_state.selected_type == "GOOD":
        st.success("✨ 【ペアトレ流】見事な水やり！特性を捉えた最高の対応です。")
    elif st.session_state.selected_type == "BAD":
        st.error("💥 【しつけ・正論の罠】世間的には正論ですが、この子には届かなかったかも…？")
    else:
        st.warning("⚠️ 【良かれと思っての罠】優しい神対応に見えて、実は成長を停滞させる栄養過多かも？")
        
    st.markdown(f"**あなたが選んだ対応:**\n> {st.session_state.selected_text}")
    st.write("---")
    
    with st.spinner("花木の様子を観察中..."):
        system_instruction = (
            "あなたは植物に例えたペアトレコーチです。プレイヤーが選んだ対応のタイプ（GOOD:ペアトレ流、BAD:お説教・正論、OVER:過保護・物のご褒美・過剰共感）"
            "に応じて、植物（子ども）の特性ゆえにどう感じて、どう変化したかを優しく解説してください。\n\n"
            "特にBADやOVERは『育児書に書いてあったり、世間一般では素晴らしいとされる対応』であるため、決してお説教をせず、"
            "『一見、ものすごく丁寧で理想的な対応に見えますよね。そうしたくなる気持ち、本当に痛いほど分かります！でも、実はこの特性の植物には……』"
            "と、親御さんの愛情に深く共感した上で、なぜ裏目に出てしまうのかをユーモラスかつ『目から鱗』の納得感で、スマホでスッと読める長さにまとめて解説してください。"
        )
        
        prompt = (
            f"トラブル内容: {st.session_state.event_title}\n"
            f"選んだ対応のタイプ: {st.session_state.selected_type}\n"
            f"実際の対応文面: {st.session_state.selected_text}"
        )
        
        model = genai.GenerativeModel(
            model_name='models/gemini-1.5-flash',
            system_instruction=system_instruction
        )
        response = model.generate_content(prompt)
        st.markdown("### 🌼 コーチからの育成アドバイス")
        st.info(response.text)
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ 同じ子で次のピンチへ挑む"):
            st.session_state.stage = "generate_event"
            st.rerun()
    with col2:
        if st.button("🔄 別の植物を新しく育てる"):
            st.session_state.stage = "select_plant"
            st.session_state.health = 50
            st.session_state.growth = "タネ・苗木"
            st.rerun()