import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 설정 및 가독성 스타일 적용
st.set_page_config(page_title="박종훈의 달러 지표", layout="centered")

@st.cache_data(ttl=86400)
def get_data():
    ticker = "USDKRW=X"
    # 최근 3년(1095일) 데이터 호출
    data = yf.download(ticker, start=datetime.now() - timedelta(days=1095))
    curr = round(float(data['Close'].iloc[-1]), 2)
    avg = round(float(data['Close'].mean()), 2)
    return curr, avg

curr, avg = get_data()

# 2. 게이지 디자인 수정 (겹침 방지 및 자동 영역 설정)
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = curr,
    number = {'suffix': "원", 'font': {'size': 50, 'color': '#2C3E50', 'family': 'Arial Black'}},
    gauge = {
        'axis': {'range': [avg*0.8, avg*1.2], 'tickwidth': 1, 'tickcolor': "#444"},
        'bar': {'color': "#2C3E50", 'thickness': 0.25},
        'bgcolor': "white",
        'borderwidth': 1,
        'bordercolor': "#ddd",
        'steps': [
            # 박종훈 기자님 기준: 평균 이하면 초록(매수), 7% 상회까지 노랑(주의), 그 이상 빨강(위험)
            {'range': [0, avg], 'color': "#00E676"},
            {'range': [avg, avg*1.07], 'color': "#FFD600"},
            {'range': [avg*1.07, 2000], 'color': "#FF5252"}],
        'threshold': {
            'line': {'color': "black", 'width': 5},
            'thickness': 0.8,
            'value': avg} # 3년 평균 지점에 검정 선 표시
    }
))

# 레이아웃 정밀 조정 (제목과 숫자 간격 확보)
fig.update_layout(
    title = {
        'text': "<b>실시간 달러 투자 지표 (박종훈 원칙)</b>", 
        'x': 0.5, 'y': 0.9, 
        'xanchor': 'center', 'yanchor': 'top',
        'font': {'size': 22, 'color': '#34495E'}
    },
    height=420, 
    margin=dict(l=40, r=40, t=100, b=20),
    paper_bgcolor = "rgba(0,0,0,0)",
)

# 3. 화면 출력
st.plotly_chart(fig, use_container_width=True)

# 상황별 박종훈 기자님 메시지 출력
if curr < avg:
    st.success(f"### ✅ 지금은 적극 매수 구간\n**박종훈 기자의 조언:** 현재 환율이 3년 평균({avg:,}원)보다 아래에 있어 안전마진이 확보된 상태입니다.")
elif curr < avg * 1.07:
    st.warning(f"### 🟡 분할 매수 및 관망\n**박종훈 기자의 조언:** 평균 환율에 근접했습니다. 무리한 비중 확대보다는 시장을 지켜볼 때입니다.")
else:
    st.error(f"### 🚨 매수 금지 및 리스크 관리\n**박종훈 기자의 조언:** 현재 환율이 평균({avg:,}원) 대비 과열권입니다. 신규 매수보다는 자산 보호에 집중하세요.")

st.caption(f"📅 데이터 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (최근 3년 이동평균 기준)")
