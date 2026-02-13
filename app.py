import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math

# 1. 페이지 설정
st.set_page_config(page_title="실시간 달러 투자 지표", layout="centered")

# 캐싱을 통해 데이터 로딩 속도 최적화
@st.cache_data(ttl=86400)
def get_data():
    try:
        ticker = "USDKRW=X"
        data = yf.download(ticker, period="3y")
        if data.empty:
            raise ValueError("데이터를 가져올 수 없습니다.")
        
        # 최신 환율 및 3년 평균 계산
        curr = round(float(data['Close'].iloc[-1]), 2)
        avg = round(float(data['Close'].mean()), 2)
        # 매수 한계 (평균 + 7%)
        limit = round(avg * 1.07, 2)
        return curr, avg, limit
    except Exception as e:
        st.error(f"데이터 로딩 오류: {e}")
        return 1400.0, 1350.0, 1444.5

curr, avg, limit = get_data()

# ==========================================
# 2. 게이지 디자인 (바늘 3개 구현)
# ==========================================

fig = go.Figure()

# 게이지 표시 범위 설정
min_scale = avg * 0.85
max_scale = avg * 1.15

# 2-1. 게이지 배경 (바늘 없이 색상띠만 배치)
fig.add_trace(go.Indicator(
    mode = "gauge", 
    value = curr,
    gauge = {
        'shape': "angular",
        'axis': {'range': [min_scale, max_scale], 'tickwidth': 2, 'tickcolor': "#333"},
        'bar': {'color': "rgba(0,0,0,0)"}, # 기본 바늘 숨김
        'bgcolor': "white",
        'steps': [
            # 형님 요청: 매수 한계(limit) 지점에서 바로 빨간색 시작
            {'range': [min_scale, avg], 'color': "#00E676"},   # 초록 (안전)
            {'range': [avg, limit], 'color': "#FFD600"},       # 노랑 (주의)
            {'range': [limit, max_scale], 'color': "#FF5252"}] # 빨강 (위험)
    }
))

# 2-2. 바늘 좌표 계산 함수 (ValueError 방지를 위해 좌표 타입 고정)
def get_needle_coords(value, min_v, max_v):
    ratio = (value - min_v) / (max_v - min_v)
    ratio = max(0.0, min(1.0, ratio))
    angle_rad = math.radians(180 - (ratio * 180))
    # 중심(0.5, 0.25) 기준 좌표
    x = 0.5 + 0.4 * math.cos(angle_rad)
    y = 0.25 + 0.4 * math.sin(angle_rad)
    return x, y

# 바늘 정보 리스트 생성 (에러 방지를 위해 하나씩 추가)
# (1) 3년 평균 (초록)
ax, ay = get_needle_coords(avg, min_scale, max_scale)
fig.add_annotation(x=ax, y=ay, ax=0.5, ay=0.25, xref='paper', yref='paper', axref='paper', ayref='paper',
                   showarrow=True, arrowhead=2, arrowwidth=3, arrowcolor='green')
fig.add_annotation(x=ax, y=ay, text=f"평균:{avg:,}", font=dict(color="green", size=11), showarrow=False, yshift=15)

# (2) 매수 한계 (빨강)
lx, ly = get_needle_coords(limit, min_scale, max_scale)
fig.add_annotation(x=lx, y=ly, ax=0.5, ay=0.25, xref='paper', yref='paper', axref='paper', ayref='paper',
                   showarrow=True, arrowhead=2, arrowwidth=3, arrowcolor='red')
fig.add_annotation(x=lx, y=ly, text=f"한계:{limit:,}", font=dict(color="red", size=11), showarrow=False, yshift=15)

# (3) 현재가 (검정, 가장 강조)
cx, cy = get_needle_coords(curr, min_scale, max_scale)
fig.add_annotation(x=cx, y=cy, ax=0.5, ay=0.25, xref='paper', yref='paper', axref='paper', ayref='paper',
                   showarrow=True, arrowhead=3, arrowwidth=5, arrowcolor='black')

# 레이아웃 마무리 (현재가 텍스트 하단 배치)
fig.update_layout(
    height=400, margin=dict(l=20, r=20, t=30, b=50),
    paper_bgcolor = "rgba(0,0,0,0)",
    annotations=list(fig.layout.annotations) + [
        dict(x=0.5, y=0, text=f"현재가: <b>{curr:,}원</b>", font=dict(size=35), showarrow=False, xref='paper', yref='paper')
    ]
)

st.plotly_chart(fig, use_container_width=True)

# 3. 하단 가이드 및 조언
st.markdown("### 📊 구간별 투자 가이드")
col1, col2, col3 = st.columns(3)
with col1: st.markdown(f"**🟢 안전 (평균 이하)**\n\n기계적 매수")
with col2: st.markdown(f"**🟡 주의 (7% 이내)**\n\n소액 적립식")
with col3: st.markdown(f"**🔴 위험 (7% 초과)**\n\n매수 중단")

st.markdown("---")

if curr < avg:
    st.success(f"### ✅ '적극 매수' 구간\n평균({avg:,}원) 아래입니다. 기계적으로 비중을 높이세요.")
elif curr < limit:
    st.warning(f"### 🟡 '적립식 대응' 구간\n평균을 넘었습니다. 소액 적립식으로만 대응하세요.")
else:
    st.error(f"### 🚨 '매수 금지' 구간\n과열권입니다. 인내하며 기회를 기다리세요.")

st.caption(f"📅 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
