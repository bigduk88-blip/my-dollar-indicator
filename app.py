import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="박종훈의 달러 지표", layout="centered")

@st.cache_data(ttl=86400)
def get_data():
    ticker = "USDKRW=X"
    data = yf.download(ticker, start=datetime.now() - timedelta(days=1095))
    curr = round(float(data['Close'].iloc[-1]), 2)
    avg = round(float(data['Close'].mean()), 2)
    limit = round(avg * 1.07, 2) # 분할매수 마지노선 (7%)
    return curr, avg, limit

curr, avg, limit = get_data()

# 2. 게이지 디자인 (기준 가격 텍스트 추가)
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = curr,
    number = {'suffix': "원", 'font': {'size': 50, 'color': '#2C3E50', 'family': 'Arial Black'}},
    gauge = {
        'axis': {'range': [avg*0.8, avg*1.2], 'tickwidth': 1},
        'bar': {'color': "#2C3E50", 'thickness': 0.25},
        'steps': [
            {'range': [0, avg], 'color': "#00E676"},   # 매수 적기
            {'range': [avg, limit], 'color': "#FFD600"}, # 분할 매수
            {'range': [limit, 2000], 'color': "#FF5252"}], # 위험
        'threshold': {
            'line': {'color': "black", 'width': 5},
            'thickness': 0.8,
            'value': avg}
    }
))

# 차트 내부에 기준 가격 주석(Annotation) 추가
fig.add_annotation(x=0.32, y=0.55, text=f"매수기준<br><b>{avg:,}원</b>", showarrow=False, font=dict(size=14, color="green"))
fig.add_annotation(x=0.68, y=0.55, text=f"마지노선<br><b>{limit:,}원</b>", showarrow=False, font=dict(size=14, color="red"))

fig.update_layout(
    title = {'text': "<b>실시간 달러 투자 지표 (박종훈 원칙)</b>", 'x': 0.5, 'y': 0.9, 'xanchor': 'center', 'font': {'size': 22}},
    height=450, margin=dict(l=40, r=40, t=100, b=20),
    paper_bgcolor = "rgba(0,0,0,0)",
)

st.plotly_chart(fig, use_container_width=True)

# 3. 상황별 박종훈 기자님의 실제 핵심 조언으로 수정
if curr < avg:
    st.success(f"### ✅ 지금은 적극 매수 구간\n**박종훈 기자의 조언:** \"환율이 3년 평균({avg:,}원)보다 낮을 때는 시장의 공포에 휘둘리지 말고 기계적으로 달러 비중을 늘려야 합니다. 지금이 바로 가장 안전한 매수 타이밍입니다.\"")
elif curr < limit:
    st.warning(f"### 🟡 분할 매수 및 관망\n**박종훈 기자의 조언:** \"평균 환율을 넘어섰지만 아직 마지노선({limit:,}원) 아래에 있습니다. 무리한 추격 매수보다는 정기적인 적립식 환전으로 리스크를 분산하며 조심스럽게 접근하세요.\"")
else:
    st.error(f"### 🚨 매수 금지 및 리스크 관리\n**박종훈 기자의 조언:** \"현재 환율은 3년 평균 대비 과열권입니다. 지금 달러를 사는 것은 상투를 잡는 지름길입니다. 신규 매수를 멈추고 환차익 수익을 즐기며 다음 기회를 기다리십시오.\"")

st.caption(f"📅 데이터 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (최근 3년 이동평균 기준)")
