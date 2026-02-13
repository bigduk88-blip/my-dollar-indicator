import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="실시간 달러 투자 지표", layout="centered")

@st.cache_data(ttl=86400)
def get_data():
    ticker = "USDKRW=X"
    data = yf.download(ticker, start=datetime.now() - timedelta(days=1095))
    curr = round(float(data['Close'].iloc[-1]), 2)
    avg = round(float(data['Close'].mean()), 2)
    limit = round(avg * 1.07, 2) 
    return curr, avg, limit

curr, avg, limit = get_data()

# 2. 게이지 디자인 (타이틀 삭제 및 레이아웃 재구성)
fig = go.Figure()

# 기본 3색 게이지 배경
fig.add_trace(go.Indicator(
    mode = "gauge+number",
    value = curr,
    number = {'suffix': "원", 'font': {'size': 60, 'color': '#2C3E50', 'family': 'Arial Black'}},
    gauge = {
        'axis': {'range': [avg*0.85, avg*1.15], 'showticklabels': False},
        'bar': {'color': "rgba(0,0,0,0.1)", 'thickness': 0.2}, # 현재 위치 살짝 표시
        'steps': [
            {'range': [0, avg], 'color': "#00E676"},   # 초록
            {'range': [avg, limit], 'color': "#FFD600"}, # 노랑
            {'range': [limit, 2000], 'color': "#FF5252"}]
    }
))

# [핵심 수정] 게이지 눈금 위에 직접 가격과 세로선 표기 (좌표 정밀 조정)
# 1. 3년 평균 가격 (초록/노랑 경계 위)
fig.add_annotation(
    x=0.48, y=0.85, 
    text=f"<b style='color:green;'>3년 평균</b><br>┃<br><b style='color:green;'>{avg:,}원</b>",
    showarrow=False, xref="paper", yref="paper", align="center"
)

# 2. 매수 한계 가격 (노랑/빨강 경계 위)
fig.add_annotation(
    x=0.72, y=0.75, 
    text=f"<b style='color:red;'>매수 한계</b><br>┃<br><b style='color:red;'>{limit:,}원</b>",
    showarrow=False, xref="paper", yref="paper", align="center"
)

# 3. 현재가 가리키는 검정 화살표 (게이지 안쪽 배치)
fig.add_annotation(
    x=0.5, y=0.45,
    text="▼", 
    showarrow=False, font=dict(size=40, color="black"),
    xref="paper", yref="paper"
)

fig.update_layout(
    height=450, 
    margin=dict(l=50, r=50, t=50, b=50), # 상단 여백 줄임 (타이틀 삭제 대응)
    paper_bgcolor = "rgba(0,0,0,0)",
)

st.plotly_chart(fig, use_container_width=True)

# 3. 구간별 가이드 및 조언 섹션
st.markdown("### 📊 구간별 투자 가이드")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**🟢 적극 매수**\n\n({avg:,}원 이하)\n\n평균가 이하 안전 구간")
with col2:
    st.markdown(f"**🟡 적립식 매수**\n\n(~ {limit:,}원)\n\n조급할 때만 소액 적립")
with col3:
    st.markdown(f"**🔴 매수 금지**\n\n({limit:,}원 초과)\n\n상투 위험 높은 고점")

st.markdown("---")

# 박종훈 기자 조언
if curr < avg:
    st.success(f"### ✅ 지금은 '적극 매수' 구간\n**박종훈 기자의 조언:** \"환율이 평균({avg:,}원) 아래일 때가 가장 안전합니다. 기계적으로 비중을 높이세요.\"")
elif curr < limit:
    st.warning(f"### 🟡 '적립식 접근' 권장\n**박종훈 기자의 조언:** \"평균을 넘었으니 무리하지 마세요. 꼭 사고 싶다면 동일 금액 적립식으로만 대응하십시오.\"")
else:
    st.error(f"### 🚨 지금은 '매수 금지' 구간\n**박종훈 기자의 조언:** \"현재 환율은 과열권입니다. 다음 기회를 위해 현금을 보유하며 인내하십시오.\"")

st.caption(f"📅 데이터 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (3년 이동평균 기준)")
