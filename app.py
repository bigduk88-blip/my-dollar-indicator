import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="박종훈의 달러 지표", layout="centered")

@st.cache_data(ttl=86400)
def get_data():
    ticker = "USDKRW=X"
    # 데이터 안정성을 위해 종가 기준 추출
    data = yf.download(ticker, start=datetime.now() - timedelta(days=3*365))
    curr = round(float(data['Close'].iloc[-1]), 2)
    avg = round(float(data['Close'].mean()), 2)
    return curr, avg

curr, avg = get_data()

# 2. 게이지 차트 (오류 수정 완료)
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = curr,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "현재 환율 vs 3년 평균", 'font': {'size': 20}},
    gauge = {
        'axis': {'range': [avg*0.8, avg*1.2], 'tickwidth': 1},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range': [0, avg], 'color': "lightgreen"},
            {'range': [avg, avg*1.1], 'color': "lemonchiffon"},
            {'range': [avg*1.1, 2000], 'color': "#ffcccb"}], # 여기 # 추가했습니다!
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': avg}
    }
))
fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))

# 3. 화면 출력
st.plotly_chart(fig, use_container_width=True)

if curr < avg:
    st.success(f"### ✅ 지금은 매수 적기!\n박종훈 기자님 기준, 현재 환율은 평균({avg:,}원)보다 낮아 안전한 구간입니다.")
else:
    st.error(f"### ⚠️ 지금은 관망 필요!\n현재 환율이 3년 평균({avg:,}원)보다 높습니다. 무리한 추격 매수는 피하세요.")

st.caption(f"최근 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (24시간 주기 갱신)")
