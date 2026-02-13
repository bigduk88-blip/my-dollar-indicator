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
    limit = round(avg * 1.07, 2) 
    return curr, avg, limit

curr, avg, limit = get_data()

# 2. 게이지 디자인 (검정 세로줄 제거 및 화살표 지표 도입)
fig = go.Figure()

# 기본 게이지 바 생성
fig.add_trace(go.Indicator(
    mode = "gauge+number",
    value = curr,
    number = {'suffix': "원", 'font': {'size': 60, 'color': '#2C3E50', 'family': 'Arial Black'}},
    gauge = {
        'axis': {'range': [avg*0.85, avg*1.15], 'tickwidth': 1, 'tickcolor': "#444"},
        'bar': {'color': "rgba(0,0,0,0)"}, # 기본 바는 투명하게 처리 (화살표로 대체)
        'bgcolor': "white",
        'borderwidth': 1,
        'bordercolor': "#ddd",
        'steps': [
            {'range': [0, avg], 'color': "#00E676"},   # 적극 매수
            {'range': [avg, limit], 'color': "#FFD600"}, # 분할 매수
            {'range': [limit, 2000], 'color': "#FF5252"}]
    }
))

# 현재가 위치를 가리키는 화살표 (▼) 추가
fig.add_annotation(
    x=0.5, y=0.45, # 게이지 곡선상의 위치를 계산하기 위해 중앙 배치 기반 조정
    text="▼", 
    showarrow=False, 
    font=dict(size=30, color="black"),
    xref="paper", yref="paper"
)

# 게이지 밖에 가격 정보 표기 (화살표 및 세로줄 효과)
# 1. 3년 평균 (매수 기준점)
fig.add_annotation(
    x=0.35, y=0.8, 
    text=f"<b>3년 평균</b><br>┃<br>{avg:,}원", 
    showarrow=False, font=dict(size=14, color="green"), align="center"
)

# 2. 매수 한계 (마지노선)
fig.add_annotation(
    x=0.65, y=0.8, 
    text=f"<b>매수 한계</b><br>┃<br>{limit:,}원", 
    showarrow=False, font=dict(size=14, color="red"), align="center"
)

# 3. 실시간 현재가 설명
fig.add_annotation(
    x=0.5, y=0.15, 
    text=f"실시간 현재가: <b>{curr:,}원</b>", 
    showarrow=False, font=dict(size=18, color="#2C3E50")
)

fig.update_layout(
    title = {'text': "<b>박종훈의 달러 투자 '전광판'</b>", 'x': 0.5, 'y': 0.95, 'xanchor': 'center', 'font': {'size': 24}},
    height=500, margin=dict(l=60, r=60, t=100, b=50),
    paper_bgcolor = "rgba(0,0,0,0)",
)

st.plotly_chart(fig, use_container_width=True)

# 3. 구간별 투자 가이드 및 조언
st.markdown("### 📊 구간별 투자 가이드")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**🟢 적극 매수**\n\n({avg:,}원 이하)\n\n가장 안전한 구간입니다. 기계적으로 비중을 늘리세요.")
with col2:
    st.markdown(f"**🟡 분할/적립 매수**\n\n({avg:,}원 ~ {limit:,}원)\n\n조급증이 날 때만 동일 금액으로 적립식 접근하세요.")
with col3:
    st.markdown(f"**🔴 매수 금지**\n\n({limit:,}원 초과)\n\n상투를 잡을 확률이 높습니다. 관망하며 기회를 기다리세요.")

st.markdown("---")

if curr < avg:
    st.success(f"### ✅ 지금은 '적극 매수' 구간입니다\n**박종훈 기자의 조언:** \"평균인 {avg:,}원 아래일 때가 가장 안전합니다. 지금 바로 달러 비중을 높이세요.\"")
elif curr < limit:
    st.warning(f"### 🟡 지금은 '조심스러운 접근'이 필요합니다\n**박종훈 기자의 조언:** \"평균을 넘었지만 사고 싶다면, 목돈이 아닌 매달 일정액만 환전하는 '적립식'으로 대응하십시오.\"")
else:
    st.error(f"### 🚨 지금은 '매수 금지' 구간입니다\n**박종훈 기자의 조언:** \"현재 환율은 과열권입니다. 신규 매수를 멈추고 현금을 보유하며 다음 기회를 인내하십시오.\"")

st.caption(f"📅 데이터 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (3년 이동평균 기준)")
