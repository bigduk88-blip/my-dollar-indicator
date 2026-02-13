import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="박종훈의 달러 지표", layout="centered")

@st.cache_data(ttl=86400)
def get_data():
    ticker = "USDKRW=X"
    # 최근 3년 데이터 호출
    data = yf.download(ticker, start=datetime.now() - timedelta(days=1095))
    curr = round(float(data['Close'].iloc[-1]), 2)
    avg = round(float(data['Close'].mean()), 2)
    limit = round(avg * 1.07, 2) 
    return curr, avg, limit

curr, avg, limit = get_data()

# 2. 게이지 디자인 (수치 텍스트 위치 정밀 조정)
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = curr,
    number = {'suffix': "원", 'font': {'size': 50, 'color': '#2C3E50', 'family': 'Arial Black'}},
    gauge = {
        'axis': {'range': [avg*0.8, avg*1.2], 'tickwidth': 1, 'tickcolor': "#444"},
        'bar': {'color': "#2C3E50", 'thickness': 0.25},
        'steps': [
            {'range': [0, avg], 'color': "#00E676"},   # 적극 매수 (초록)
            {'range': [avg, limit], 'color': "#FFD600"}, # 분할 매수 (노랑)
            {'range': [limit, 2000], 'color': "#FF5252"}], # 매수 금지 (빨강)
        'threshold': {
            'line': {'color': "black", 'width': 6},
            'thickness': 0.8,
            'value': avg}
    }
))

# 텍스트 주석 위치 재조정 (겹침 방지)
# 현재 가격 텍스트를 숫자 바로 위가 아닌, 더 아래쪽 여백으로 내렸습니다.
fig.add_annotation(x=0.5, y=-0.05, text=f"실시간 현재가: <b>{curr:,}원</b>", showarrow=False, font=dict(size=18, color="#2C3E50"))
fig.add_annotation(x=0.25, y=0.5, text=f"3년 평균<br><b>{avg:,}원</b>", showarrow=False, font=dict(size=14, color="green"))
fig.add_annotation(x=0.75, y=0.5, text=f"매수 한계<br><b>{limit:,}원</b>", showarrow=False, font=dict(size=14, color="red"))

fig.update_layout(
    title = {'text': "<b>실시간 달러 투자 지표 (박종훈 원칙)</b>", 'x': 0.5, 'y': 0.95, 'xanchor': 'center', 'font': {'size': 22}},
    height=500, # 높이를 충분히 확보하여 아래쪽 텍스트 공간 마련
    margin=dict(l=50, r=50, t=100, b=80), # 아래쪽(b) 여백을 늘려 현재가 표시 공간 확보
    paper_bgcolor = "rgba(0,0,0,0)",
)

st.plotly_chart(fig, use_container_width=True)

# 3. 구간별 투자 가이드 (디자인 유지)
st.markdown("### 📊 구간별 투자 가이드")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**🟢 적극 매수**\n\n({avg:,}원 이하)\n\n가장 안전한 구간입니다. 기계적으로 비중을 늘리세요.")
with col2:
    st.markdown(f"**🟡 분할/적립 매수**\n\n({avg:,}원 ~ {limit:,}원)\n\n조급증이 날 때만 동일 금액으로 적립식 접근하세요.")
with col3:
    st.markdown(f"**🔴 매수 금지**\n\n({limit:,}원 초과)\n\n상투를 잡을 확률이 높습니다. 관망하며 기회를 기다리세요.")

st.markdown("---")

# 4. 박종훈 기자 조언
if curr < avg:
    st.success(f"### ✅ 지금은 '적극 매수' 구간입니다\n**박종훈 기자의 조언:** \"환율이 평균인 {avg:,}원 아래일 때가 가장 안전합니다. 공포를 이기고 달러 비중을 높이세요.\"")
elif curr < limit:
    st.warning(f"### 🟡 지금은 '조심스러운 접근'이 필요합니다\n**박종훈 기자의 조언:** \"평균을 넘었지만 사고 싶은 마음이 크다면, 목돈이 아닌 매달 일정한 금액만 환전하는 '적립식'으로 대응하십시오.\"")
else:
    st.error(f"### 🚨 지금은 '매수 금지' 구간입니다\n**박종훈 기자의 조언:** \"현재 환율은 과열권입니다. 신규 매수를 멈추고 다음 기회를 위해 현금을 보유하며 인내하십시오.\"")

st.caption(f"📅 데이터 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (3년 이동평균 기준)")
