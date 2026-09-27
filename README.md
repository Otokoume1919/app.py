# app.py
import streamlit as st

# ==========================================
# ページ基本設定（スマホ表示に最適化）
# ==========================================
st.set_page_config(
    page_title="競馬クオンツ基盤 Ver.3.1a",
    page_icon="🏇",
    layout="centered",  # スマホで見やすい中央寄りの1カラムレイアウト
    initial_sidebar_state="collapsed" # スマホではサイドバーを初期折りたたみ
)

st.title("🏇 競馬クオンツ基盤 Ver.3.1a")
st.caption("秋華賞用 本番モデル（データ品質ゲート搭載）")

# ==========================================
# 1. Model Config 設定（キー参照設計）
# ==========================================
# 本来はDBやConfigファイルから読み込みます
config = {
    "RACE_BUY_SCORE_MIN": 60,
    "EV_MIN": 1.05,             # EV閾値 (1.05以上でBET対象)
    "KELLY_FRACTION": 0.25,       # クォーターケリー
    "MAX_RACE_EXPOSURE": 0.10,    # 1レース最大許容資金比率 (10%)
    "HIGH_CONFIDENCE_MIN": 70,
    "UNCERTAINTY_MAX": 30,
    "BANKROLL": 100000            # 総資金（円）
}

# サイドバーに設定確認画面を配置
with st.sidebar:
    st.header("⚙️ Model Config")
    st.json(config)

# ==========================================
# 2. データ入力エリア（レース & 馬券情報）
# ==========================================
st.subheader("1. レース・事前データ入力")

with st.expander("📝 データ入力フォームを開く", expanded=True):
    race_name = st.text_input("レース名", value="2026年 秋華賞 (G1)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        odds = st.number_input("単勝 / 買目オッズ", min_value=1.0, value=4.5, step=0.1)
    with col_b:
        p1 = st.number_input("P1 (一次評価確率 %)", min_value=0.0, max_value=100.0, value=30.0) / 100.0

    st.markdown("**シナリオ別確率設定 (Low ≤ Base ≤ High)**")
    c1, c2, c3 = st.columns(3)
    with c1:
        p_low = st.number_input("Low (%)", value=20.0) / 100.0
    with c2:
        p_base = st.number_input("Base (%)", value=28.0) / 100.0
    with c3:
        p_high = st.number_input("High (%)", value=35.0) / 100.0

    p3 = st.number_input("P3 (最終モデル予測確率 %)", min_value=0.0, max_value=100.0, value=28.0) / 100.0
    
    is_result_entered = st.checkbox("レース結果確定済み（着順入力完了）", value=False)

# ==========================================
# 3. データ完全性チェック（ゲート構造ロジック）
# ==========================================
def check_data_quality():
    errors = []
    
    # 確率の0~100%範囲チェック
    if not (0 <= p1 <= 1 and 0 <= p3 <= 1):
        errors.append("確率(P1/P3)が 0%〜100% の範囲外です。")
    
    # シナリオ順序チェック (Low <= Base <= High)
    if not (p_low <= p_base <= p_high):
        errors.append("シナリオ不整合: Low ≤ Base ≤ High になっていません。")
        
    # オッズチェック
    if odds <= 1.0:
        errors.append("有効なオッズが入力されていません。")

    if errors:
        return "INCOMPLETE", errors
    elif not is_result_entered:
        return "RESULT PENDING", []
    else:
        return "DATA READY", []

status, error_messages = check_data_quality()

# ==========================================
# 4. データ品質バッジ & ゲート判定表示
# ==========================================
st.subheader("2. データ品質ステータス")

if status == "DATA READY":
    st.success("🟢 STATUS: DATA READY （データ完全性クリア・計算有効）")
elif status == "RESULT PENDING":
    st.info("🟡 STATUS: RESULT PENDING （事前データ確認完了・結果待ち）")
else:
    st.error("🔴 STATUS: INCOMPLETE （入力不備あり・計算ブロック中）")
    for msg in error_messages:
        st.caption(f"⚠️ {msg}")

# ==========================================
# 5. モデル計算 & EV / Kelly 判定
# ==========================================
st.subheader("3. 計算結果 & BET/PASS 判定")

# ゲート通過チェック: INCOMPLETE の場合は計算・判定を遮断
if status == "INCOMPLETE":
    st.warning("⛔ データが不完全なため、BET判定を出力できません。入力内容を修正してください。")
else:
    # ① 期待値（EV）計算
    ev = odds * p3
    
    # ② Kelly 基準計算 (b = odds - 1, p = p3, q = 1 - p3)
    b = odds - 1.0
    kelly_full = (b * p3 - (1.0 - p3)) / b if b > 0 else 0
    kelly_full = max(0.0, kelly_full) # 負の値は0にする
    
    # Fractional Kelly & 指数上限制限
    kelly_suggested = kelly_full * config["KELLY_FRACTION"]
    max_exposure = config["MAX_RACE_EXPOSURE"]
    final_kelly_ratio = min(kelly_suggested, max_exposure)
    
    bet_amount = int(config["BANKROLL"] * final_kelly_ratio)
    
    # ③ 最終 BET / PASS 判定
    is_bet = (ev >= config["EV_MIN"]) and (bet_amount > 0)
    
    # スマホ向けカード型 UI 表示
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric("期待値 (EV)", f"{ev:.2f}", delta=f"{ev - 1.0:+.2f}")
    with col_res2:
        st.metric("推奨賭け率", f"{final_kelly_ratio*100:.1f}%")

    st.markdown("---")
    
    if is_bet:
        st.success(f"🎯 **判定: BET** (推奨購入額: **{bet_amount:,} 円**)")
    else:
        st.error("✋ **判定: PASS** (購入基準を満たしていません)")

    # 詳細分析アコーディオン
    with st.expander("📊 シナリオ別 EV 分析"):
        st.write(f"- Low シナリオ EV: **{odds * p_low:.2f}**")
        st.write(f"- Base シナリオ EV: **{odds * p_base:.2f}**")
        st.write(f"- High シナリオ EV: **{odds * p_high:.2f}**")
