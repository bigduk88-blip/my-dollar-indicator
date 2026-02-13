import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math # 바늘 좌표 계산을 위한 수학 모듈 추가

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

# ==========================================
# 2. 게이지 디자인 (바늘 3개 구현 핵심 로직)
# ==========================================

fig = go.Figure()

# 게이지 표시 범위 설정 (평균 기준 ±20% 정도로 설정)
min_scale = avg * 0.8
max_scale = avg * 1.2

# 2-1. 기본 게이지 배경 그리기 (바늘 없이 배경만)
fig.add_trace(go.Indicator(
    mode = "gauge", # 숫자 표시 없이 순수 게지만
    value = curr,   # 이 값은 실제로는 표시 안 함 (바늘 로직 따로 구현)
    gauge = {
        'shape': "angular",
        'axis': {'range': [min_scale, max_scale], 'tickwidth': 2, 'tickcolor': "#333", 'tickfont': {'size': 15}},
        'bar': {'color': "rgba(0,0,0,0)"}, # 기본 바늘 숨김
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "#eee",
        'steps': [
            {'range': [min_scale, avg], 'color': "#00E676"},   # 초록(안전)
            {'range': [avg, limit], 'color': "#FFD600"}, # 노랑(주의)
            {'range': [limit, max_scale], 'color': "#FF5252"}] # 빨강(위험)
    }
))

# 2-2. 바늘 좌표 계산 헬퍼 함수 (삼각함수 활용)
def get_arrow_coords(value, min_v, max_v, radius=0.4):
    # 값을 0~1 비율로 변환
    ratio = (value - min_v) / (max_v - min_v)
    ratio = max(0, min(1, ratio)) # 범위 밖 값 보정
    # 각도 계산 (Plotly 게이지는 180도(좌)에서 0도(우)로 이동)
    angle_deg = 180 - (ratio * 180)
    angle_rad = math.radians(angle_deg)
    # 중심점(0.5, 0.25) 기준 바늘 끝 좌표 계산
    center_x, center_y = 0.5, 0.25
    tip_x = center_x + radius * math.cos(angle_rad)
    tip_y = center_y + radius * math.sin(angle_rad)
    return tip_x, tip_y

# 2-3. 바늘 3개 그리기 (Annotation 화살표 활용)

# (1) 3년 평균 바늘 (초록색)
ax, ay = get_arrow_coords(avg, min_scale, max_scale)
fig.add_annotation(x=ax, y=ay, ax=0.5, ay=0.25, xref='paper', yref='paper', axref='paper', ayref='paper',
                   showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=4, arrowcolor='green', opacity=0.7)
fig.add_annotation(x=ax, y=ay, text=f"<b>3년평균</b><br>{avg:,}", font=dict(color="green", size=13), showarrow=False, yshift=25, xref='paper', yref='paper')

# (2) 매수 한계 바늘 (빨간색)
lx, ly = get_arrow_coords(limit, min_scale, max_scale)
fig.add_annotation(x=lx, y=ly, ax=0.5, ay=0.25, xref='paper', yref='paper', axref='paper', ayref='paper',
                   showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=4, arrowcolor='red', opacity=0.7)
fig.add_annotation(x=lx, y=ly, text=f"<b>매수한계</b><br>{limit:,}", font=dict(color="red", size=13), showarrow=False, yshift=25, xref='paper', yref='paper')

# (3) 현재가 바늘 (검정색, 가장 두껍게 강조)
cx, cy = get_arrow_coords(curr, min_scale, max_scale)
fig.add_annotation(x=cx, y=cy, ax=0.5, ay=0.25, xref='paper', yref='paper', axref='paper', ayref='paper',
                   showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=6, arrowcolor='black')
# 현재가 텍스트는 중앙 하단에 크게 표시
fig.add_annotation(x=0.5, y=0.1, text=f"현재가: <b>{curr:,}원</b>", font=dict(color="black", size=30), showarrow=False, xref='paper', yref='paper')


# 레이아웃 조정 (타이틀 제거, 여백 최적화)
fig.update_layout(
    height=450,
    margin=dict(l=30, r=30, t=30, b=80),
    paper_bgcolor = "rgba(0,0,0,0)",
    font={'family': "Arial, sans-serif"}
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. 하단 가이드 및 조언
# ==========================================

st.markdown("### 📊 구간별 투자 가이드")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**🟢 안전 구간 (평균 이하)**\n\n기계적 분할 매수 적기")
with col2:
    st.markdown(f"**🟡 주의 구간 (~7% 상회)**\n\n조급할 때만 소액 적립")
with col3:
    st.markdown(f"**🔴 위험 구간 (7% 초과)**\n\n매수 중단, 관망 필요")

st.markdown("---")

# 박종훈 기자 조언
if curr < avg:
    st.success(f"### ✅ 지금은 '적극 매수' 구간\n**박종훈 기자의 조언:** \"환율이 평균({avg:,}원) 아래일 때가 가장 안전합니다. 공포를 이기고 기계적으로 비중을 높이세요.\"")
elif curr < limit:
    st.warning(f"### 🟡 '적립식 접근' 권장\n**박종훈 기자의 조언:** \"평균을 넘었으니 무리하지 마세요. 꼭 사고 싶다면 동일 금액 적립식으로만 대응하십시오.\"")
else:
    st.error(f"### 🚨 지금은 '매수 금지' 구간\n**박종훈 기자의 조언:** \"현재 환율은 과열권입니다. 신규 매수를 멈추고 다음 기회를 위해 현금을 보유하며 인내하십시오.\"")

st.caption(f"📅 데이터 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (최근 3년 이동평균 기준)")
