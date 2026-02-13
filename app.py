import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 설정 및 배경색 최적화
st.set_page_config(page_title="박종훈의 달러 지표", layout="centered")

# CSS를 이용해 전체적인 가독성 상향 (글자 선명도)
st.markdown("""
    <style>
    .main { font-family: 'Pretendard', sans-serif; }
    div[data-testid="stMetricValue"] { font-size: 30px; font-weight: 700; color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=86400)
def get_data():
    ticker = "USDKRW=X"
    data = yf.download(ticker, start=datetime.now() - timedelta(days=3*365))
    curr = round(float(data['Close'].iloc[-1]), 2)
    avg = round(float(data['Close'].mean()), 2)
    return curr, avg

curr, avg = get_data()

# 2. 게이지 디자인 업그레이드 (대비 강화)
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = curr,
    number = {'suffix': "원", 'font': {'size': 60, 'color': '#2C3E50', 'family': 'Arial Black'}},
    gauge = {
        'axis': {'range': [avg*0.85, avg*1.15], 'tickwidth': 2, 'tickcolor': "#444"},
        'bar': {'color': "#2C3E50", 'thickness': 0.3}, # 바 두께 조절로 선명함 추가
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "#ddd",
        'steps': [
            {'range': [0, avg], 'color': "#00E676"},   # 더 선명한 초록
            {'range': [avg, avg*1.07], 'color': "#FFD600"}, # 더 선명한 노랑
            {'range': [avg*1.07, 2000], 'color': "#FF5252"}], # 더 선명한 빨강
        'threshold': {
            'line': {'color': "black", 'width': 5},
            'thickness': 0.8,
            'value': avg}
    }
))

fig.update_layout(
    title = {'text': "<b>실시간 달러 투자 지표</b>", 'x': 0.5, 'y': 0.85, 'font': {'size': 24, 'color': '#34495E'}},
    height=400, 
    margin=dict(l=30, r=30, t=80, b=20),
    paper_bgcolor = "rgba(0,0,0,0)", # 배경 투명화로 블로그와 동화
)

# 3. 화면 출력
st.plotly_chart(fig, use_container_width=True)

# 박종훈의 Tip 섹션 디자인 강화
if curr < avg:
    st.success(f"### ✅ 지금은 적극 매수 구간\n**박종훈 기자의 조언:** 현재 환율이 3년 평균({avg:,}원)보다 아래에 있어 안전마진이 확보된 상태입니다.")
elif curr < avg * 1.07:
    st.warning(f"### 🟡 분할 매수 및 관망\n**박종훈 기자의 조언:** 평균 환율에 근접했습니다. 무리한 비중 확대보다는 시장을 지켜볼 때입니다.")
else:
    st.error(f"### 🚨 매수 금지 및 리스크 관리\n**박종훈 기자의 조언:** 현재 환율이 평균({avg:,}원) 대비 과열권입니다. 신규 매수보다는 자산 보호에 집중하세요.")

st.caption(f"📅 데이터 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (3년 이동평균 기준)")
