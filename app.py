import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="NEXUS RACING", page_icon="◆", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
:root{--bg:#0b1020;--panel:#1a1033;--cyan:#00f5ff;--pink:#ff2bd6;--purple:#7c3cff;--text:#e9f1ff;--soft:#9aa8c7}
.stApp{background:radial-gradient(circle at 15% 0%,rgba(124,60,255,.16),transparent 30%),radial-gradient(circle at 100% 15%,rgba(0,245,255,.08),transparent 25%),var(--bg);color:var(--text)}
.block-container{max-width:1180px;padding-top:1rem;padding-bottom:7rem}
h1,h2,h3,p,label{color:var(--text)!important}
.nr-brand{font-size:1.25rem;font-weight:900;letter-spacing:.12em}.nr-brand span{color:var(--cyan)}
.nr-sub,.muted{color:var(--soft);font-size:.78rem}
.card{background:linear-gradient(145deg,rgba(26,16,51,.94),rgba(17,24,43,.97));border:1px solid rgba(233,241,255,.1);border-radius:19px;padding:16px;margin:10px 0;box-shadow:0 14px 35px rgba(0,0,0,.23)}
.primary{border-color:rgba(0,245,255,.35)}
.badge{display:inline-block;padding:5px 10px;border-radius:999px;font-size:.72rem;font-weight:800}
.buy{color:var(--cyan);border:1px solid rgba(0,245,255,.5);background:rgba(0,245,255,.12)}
.wait{color:#d6a9ff;border:1px solid rgba(180,92,255,.5);background:rgba(180,92,255,.12)}
.pass{color:#aeb9d2;border:1px solid rgba(174,185,210,.25);background:rgba(174,185,210,.08)}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:9px;margin-top:10px}.kv{background:rgba(255,255,255,.025);padding:10px;border-radius:12px}.kv small{color:var(--soft)}.kv b{display:block;font-size:1.1rem;margin-top:2px}
.cyan{color:var(--cyan)}.rule{height:1px;background:rgba(233,241,255,.1);margin:12px 0}
div[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(26,16,51,.92),rgba(17,24,43,.96));border:1px solid rgba(233,241,255,.1);border-radius:17px;padding:12px}
div[data-testid="stMetricValue"]{color:var(--cyan)!important}
.stButton>button{width:100%;min-height:48px;border-radius:14px;color:var(--text);border:1px solid rgba(0,245,255,.34);background:linear-gradient(100deg,rgba(124,60,255,.3),rgba(255,43,214,.16))}
[data-testid="stExpander"]{background:rgba(17,24,43,.75);border:1px solid rgba(233,241,255,.1);border-radius:15px}
.bottom{position:fixed;z-index:999;bottom:0;left:0;right:0;background:rgba(11,16,32,.96);backdrop-filter:blur(14px);border-top:1px solid rgba(0,245,255,.13);padding:7px}.nav{max-width:700px;margin:auto;display:grid;grid-template-columns:repeat(5,1fr)}.nav div{text-align:center;color:#8794b2;font-size:.66rem;padding:5px 0}.nav .on{color:var(--cyan)}.nav b{display:block;font-size:1rem}
@media(max-width:700px){.block-container{padding-left:.72rem;padding-right:.72rem;padding-top:.6rem}.card{padding:14px}.stRadio [role="radiogroup"]{gap:.2rem}}
</style>
""", unsafe_allow_html=True)

CONFIG={"最低期待値":1.15,"購入判定スコア":80,"ケリー係数":0.25,"1レース最大投資率":0.05,"運用資金":100000}

@st.cache_data(ttl=300)
def data():
    races=pd.DataFrame([
      ["R001","中山","11R","サンプルG1","GⅠ","購入候補",1.31,86,"ワイド ⑥－⑯",2000],
      ["R002","阪神","11R","サンプル重賞","GⅢ","オッズ待ち",1.12,81,"ワイド ③－⑧",0],
      ["R003","中山","10R","サンプル特別","","見送り",.94,58,"－",0]],
      columns=["id","場","R","レース名","格","判定","最大期待値","購入スコア","推奨","推奨額"])
    horses=pd.DataFrame([
      ["R001",7,"サンプルホースA","堅軸候補",4.2,.248,.612,.058,1.34],
      ["R001",12,"サンプルホースB","穴候補",18.6,.081,.294,.043,1.26],
      ["R001",3,"サンプルホースC","危険人気馬",3.8,.180,.451,-.051,1.08]],
      columns=["race_id","馬番","馬名","評価","現在オッズ","勝率","3着内率","市場乖離","期待値"])
    bets=pd.DataFrame([
      ["R001","ワイド","⑥－⑯",7.2,6.4,1.31,2000,"購入候補"],
      ["R001","3連複","③－⑥－⑯",28.4,24.7,1.18,800,"購入候補"],
      ["R001","馬連","⑥－⑦",8.0,8.4,1.09,0,"オッズ待ち"]],
      columns=["race_id","券種","買い目","現在オッズ","最低オッズ","期待値","推奨額","判定"])
    hist=pd.DataFrame([["G1","ワイド",48,17,.331],["G2","ワイド",61,19,.298],["G3","3連複",54,9,.194]],columns=["区分","券種","予測件数","的中","予測平均"])
    return races,horses,bets,hist

races,horses,bets,hist=data()
if "updated" not in st.session_state: st.session_state.updated=datetime.now().strftime("%m/%d %H:%M")

def badge(x):
    c={"購入候補":"buy","オッズ待ち":"wait","見送り":"pass"}.get(x,"pass")
    return f'<span class="badge {c}">{x}</span>'

def race_card(r,primary=False):
    st.markdown(f"""<div class="card {'primary' if primary else ''}">
    <div class="muted">{r['場']} {r['R']}　{r['格']}</div><div style="font-size:1.08rem;font-weight:800;margin:4px 0 9px">{r['レース名']}</div>{badge(r['判定'])}
    <div class="grid"><div class="kv"><small>最大期待値</small><b class="cyan">{r['最大期待値']:.2f}</b></div><div class="kv"><small>購入スコア</small><b>{r['購入スコア']}</b></div></div>
    <div class="rule"></div><small class="muted">推奨買い目</small><br><b>{r['推奨']}</b><b style="float:right">¥{r['推奨額']:,}</b></div>""",unsafe_allow_html=True)

def refresh():
    st.session_state.updated=datetime.now().strftime("%m/%d %H:%M:%S")
    st.cache_data.clear()

with st.sidebar:
    st.markdown("### 設定")
    st.caption("通常は変更不要")
    for k,v in CONFIG.items(): st.write(f"**{k}**　{v}")

st.markdown('<div class="nr-brand"><span>NEXUS</span> RACING</div><div class="nr-sub">QUANTITATIVE RACE ANALYTICS</div>',unsafe_allow_html=True)
page=st.radio("画面",["ホーム","レース分析","購入判断","分析実績","モデル検証"],horizontal=True,label_visibility="collapsed")

if page=="ホーム":
    st.markdown("## 今日の判断")
    st.caption("買うべきレースと、買い目・金額を最短で確認")
    if st.button("↻ 最新情報に更新"):
        with st.spinner("最新情報を確認しています…"): refresh()
        st.success("更新しました。※現在はサンプルデータ。実取得処理の接続口です。")
    st.caption(f"最終更新　{st.session_state.updated}")
    buy=races[races["判定"]=="購入候補"]
    if len(buy):
        st.markdown("### 本日の勝負候補"); race_card(buy.sort_values("最大期待値",ascending=False).iloc[0],True)
    st.markdown("### 本日の分析レース")
    only=st.toggle("勝負候補だけ表示")
    for _,r in (races[races["判定"]!="見送り"] if only else races).iterrows(): race_card(r)
    with st.expander("データ取得状況"):
        st.write("出馬表　● 取得済み"); st.write("過去走　● 取得済み"); st.write(f"現在オッズ　● {st.session_state.updated} 更新"); st.write("馬場状態　● 取得済み"); st.write("レース結果　─ レース前"); st.write("過去モデル　● 同期済み")

elif page=="レース分析":
    st.markdown("## レース分析")
    opts={f"{r['場']} {r['R']}｜{r['レース名']}":r["id"] for _,r in races.iterrows()}
    label=st.selectbox("分析するレース",list(opts)); rid=opts[label]; rr=races[races.id==rid].iloc[0]; race_card(rr,True)
    rh=horses[horses.race_id==rid]
    if rh.empty: st.info("このレースの馬データはまだありません。")
    for _,h in rh.iterrows():
        st.markdown(f"""<div class="card"><b>{int(h['馬番'])}番　{h['馬名']}</b><div style="margin:7px 0">{badge('購入候補' if h['評価']=='堅軸候補' else 'オッズ待ち' if h['評価']=='穴候補' else '見送り')} <span class="muted">{h['評価']}</span></div>
        <div class="grid"><div class="kv"><small>現在オッズ</small><b>{h['現在オッズ']:.1f}倍</b></div><div class="kv"><small>勝率</small><b>{h['勝率']:.1%}</b></div><div class="kv"><small>3着内率</small><b>{h['3着内率']:.1%}</b></div><div class="kv"><small>市場との乖離</small><b class="cyan">{h['市場乖離']:+.1%}</b></div></div></div>""",unsafe_allow_html=True)
        with st.expander(f"{h['馬名']} の詳細を見る"):
            for x in ["過去走","ラップ適性","コース適性","展開適性","枠","ローテーション","リスク要因","総合評価理由"]: st.write(f"**{x}**　実データ接続後に表示")
    if not rh.empty:
        st.markdown("### 各馬の期待値"); st.bar_chart(rh.set_index("馬名")[["期待値"]],horizontal=True)
        with st.expander("全頭を縦一覧で見る"):
            for _,h in rh.sort_values("馬番").iterrows(): st.write(f"**{int(h['馬番'])}番 {h['馬名']}**｜{h['現在オッズ']:.1f}倍｜勝率 {h['勝率']:.1%}｜3着内 {h['3着内率']:.1%}｜乖離 {h['市場乖離']:+.1%}")

elif page=="購入判断":
    st.markdown("## 購入判断")
    opts={f"{r['場']} {r['R']}｜{r['レース名']}":r["id"] for _,r in races.iterrows()}
    label=st.selectbox("対象レース",list(opts)); rid=opts[label]; rb=bets[bets.race_id==rid]
    if rb.empty: st.info("現在、このレースに推奨買い目はありません。")
    for i,(_,b) in enumerate(rb.iterrows(),1):
        st.markdown(f"""<div class="card {'primary' if b['判定']=='購入候補' else ''}"><small class="muted">推奨 {i:02d}</small><div style="font-size:1.35rem;font-weight:900">{b['券種']}　{b['買い目']}</div><div style="margin:7px 0">{badge(b['判定'])}</div><div class="grid"><div class="kv"><small>現在オッズ</small><b>{b['現在オッズ']:.1f}倍</b></div><div class="kv"><small>最低購入オッズ</small><b>{b['最低オッズ']:.1f}倍</b></div><div class="kv"><small>期待値</small><b class="cyan">{b['期待値']:.2f}</b></div><div class="kv"><small>モデル推奨</small><b>¥{int(b['推奨額']):,}</b></div></div></div>""",unsafe_allow_html=True)
    st.markdown("### 購入シミュレーション")
    budget=st.number_input("今回の予算",min_value=0,value=5000,step=1000)
    buys=rb[rb["判定"]=="購入候補"].copy(); total=int(buys["推奨額"].sum()) if len(buys) else 0
    if total:
        scale=min(1,budget/total); alloc=buys["推奨額"]*scale; used=float(alloc.sum()); ret=float((alloc*buys["期待値"]).sum()); profit=ret-used
        a,b=st.columns(2); a.metric("想定配分",f"¥{used:,.0f}"); b.metric("期待払戻",f"¥{ret:,.0f}")
        a,b=st.columns(2); a.metric("期待利益",f"¥{profit:,.0f}"); b.metric("期待利益率",f"{profit/used if used else 0:.1%}")
        if budget>total: st.warning(f"入力予算はモデル推奨総額 ¥{total:,} を上回っています。超過分は配分しません。")
    with st.expander("見送り・オッズ待ちの理由"):
        for _,b in rb[rb["判定"]!="購入候補"].iterrows(): st.write(f"**{b['券種']} {b['買い目']}**｜現在オッズ {b['現在オッズ']:.1f}倍 / 最低 {b['最低オッズ']:.1f}倍")

elif page=="分析実績":
    st.markdown("## 分析実績"); st.caption("実購入収支ではなく、モデル予測と結果の一致度を検証")
    total=int(hist["予測件数"].sum()); hits=int(hist["的中"].sum()); hr=hits/total if total else 0; pred=(hist["予測件数"]*hist["予測平均"]).sum()/total if total else 0
    a,b=st.columns(2); a.metric("推奨買い目",f"{total}件"); b.metric("的中",f"{hits}件")
    a,b=st.columns(2); a.metric("的中率",f"{hr:.1%}"); b.metric("予測平均との差",f"{hr-pred:+.1%}")
    a,b=st.columns(2)
    with a: st.selectbox("対象",["全重賞","G1","G2","G3"])
    with b: st.selectbox("券種",["全券種","単勝","複勝","枠連","馬連","馬単","ワイド","3連複","3連単"])
    d=hist.copy(); d["実際の的中率"]=d["的中"]/d["予測件数"]; d["予測的中率"]=d["予測平均"]
    st.markdown("### 予測と結果の乖離"); st.bar_chart(d.set_index("区分")[["予測的中率","実際の的中率"]])

else:
    st.markdown("## モデル検証"); st.caption("専門的な検証情報はここに集約")
    a,b=st.columns(2); a.metric("モデル","Ver.3.1a"); b.metric("検証サンプル",f"{int(hist['予測件数'].sum())}件")
    st.markdown('<div class="card primary"><small class="muted">検証ポリシー</small><br><b>事前予測はレース終了後に変更しない</b><div class="rule"></div><span class="muted">50レース：精度確認 ／ 100レース：確率校正 ／ 200レース：モデル構造レビュー</span></div>',unsafe_allow_html=True)
    st.info("Brier Score・確率校正・G1/重賞別・券種別精度を、実データ蓄積後に接続します。")
    with st.expander("データ更新・照合フロー"):
        for x in ["最新データ取得","データ完全性確認","モデル分析・期待値計算","事前予測を固定","レース終了後に結果取得","予測と結果を自動照合","モデル検証データへ追加"]: st.write("・"+x)

items=[("⌂","ホーム"),("◇","レース分析"),("◎","購入判断"),("▣","分析実績"),("⌁","モデル検証")]
nav='<div class="bottom"><div class="nav">'+''.join(f'<div class="{"on" if l==page else ""}"><b>{i}</b>{l}</div>' for i,l in items)+'</div></div>'
st.markdown(nav,unsafe_allow_html=True)

