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
            raise ValueError("데이터 없음")
        
        curr = round(float(data['Close'].iloc[-1]), 2)
        avg = round(float(data['Close'].mean()), 2)
        limit = round(avg * 1.07, 2)
        return curr, avg, limit
    except Exception:
        return 1400.0, 1350.0, 1444.5

curr, avg, limit = get_data()

# ==========================================
# 2. 게이지 디자인 (직선 Shape 방식)
# ==========================================

fig = go.Figure()

# 범위 설정
min_scale = avg * 0.85
max_scale = avg * 1.15

# 2-1. 게이지 배경 (바늘 없이 색상띠만)
fig.add_trace(go.Indicator(
    mode = "gauge", 
    value = curr,
    gauge = {
        'shape': "angular",
        'axis': {'range': [min_scale, max_scale], 'tickwidth': 2, 'tickcolor': "#333"},
        'bar': {'color': "rgba(0,0,0,0)"}, # 기본 바늘 숨김
        'bgcolor': "white",
        'steps': [
            {'range': [min_scale, avg], 'color': "#00E676"},   # 초록
            {'range': [avg, limit], 'color': "#FFD600"},       # 노랑
            {'range': [limit, max_scale], 'color': "#FF5252"}] # 빨강
    }
))

# 2-2. 바늘 좌표 계산 함수 (직선 그리기용)
def get_needle_tip(value, min_v, max_v, radius=0.4):
    try:
        ratio = (value - min_v) / (max_v - min_v)
        ratio = max(0.0, min(1.0, ratio))
    except:
        ratio = 0.5
    
    # 180도(좌) ~ 0도(우)
    angle_rad = math.radians(180 - (ratio * 180))
    
    # 중심점(0.5, 0.25) 기준 끝점 계산
    x = 0.5 + radius * math.cos(angle_rad)
    y = 0.25 + radius * math.sin(angle_rad)
    return x, y

# 2-3. 바늘 3개 그리기 (Line Shape 사용 - 에러 없음)

# (1) 3년 평균 (초록색 얇은 바늘)
gx, gy = get_needle_tip(avg, min_scale, max_scale, 0.42)
fig.add_shape(type="line", x0=0.5, y0=0.25, x1=gx, y1=gy,
              line=dict(color="green", width=3), xref="paper", yref="paper")
fig.add_annotation(x=gx, y=gy, text=f"평균<br>{avg:,.0f}", showarrow=False, 
                   font=dict(color="green", size=12), yshift=20, xref="paper", yref="paper")

# (2) 매수 한계 (빨간색 얇은 바늘)
rx, ry = get_needle_tip(limit, min_scale, max_scale, 0.42)
fig.add_shape(type="line", x0=0.5, y0=0.25, x1=rx, y1=ry,
              line=dict(color="red", width=3), xref="paper", yref="paper")
fig.add_annotation(x=rx, y=ry, text=f"한계<br>{limit:,.0f}", showarrow=False, 
                   font=dict(color="red", size=12), yshift=20, xref="paper", yref="paper")

# (3) 현재가 (검정색 굵은 바늘)
cx, cy = get_needle_tip(curr, min_scale, max_scale, 0.45) # 조금 더 길게
fig.add_shape(type="line", x0=0.5, y0=0.25, x1=cx, y1=cy,
              line=dict(color="black", width=6), xref="paper", yref="paper")

# (4) 바늘 중심축 (원형)
fig.add_shape(type="circle", x0=0.48, y0=0.23, x1=0.52, y1=0.27,
              fillcolor="black", line_color="black", xref="paper", yref="paper")

# 레이아웃 마무리
fig.update_layout(
    height=400, margin=dict(l=20, r=20, t=40, b=50),
    paper_bgcolor = "rgba(0,0,0,0)",
    annotations=list(fig.layout.annotations) + [
        dict(x=0.5, y=0, text=f"현재가: <b>{curr:,}원</b>", font=dict(size=30, color="black"), showarrow=False, xref='paper', yref='paper')
    ]
)

st.plotly_chart(fig, use_container_width=True)

# 3. 하단 가이드
st.markdown("### 📊 구간별 투자 가이드")
col1, col2, col3 = st.columns(3)
with col1: st.markdown(f"**🟢 안전 (평균 이하)**\n\n기계적 매수")
with col2: st.markdown(f"**🟡 주의 (7% 이내)**\n\n소액 적립식")
with col3: st.markdown(f"**🔴 위험 (7% 초과)**\n\n매수 중단")

st.markdown("---")

if curr < avg:
    st.success(f"### ✅ '적극 매수' 구간\n현재 {curr:,}원은 평균({avg:,}원)보다 낮습니다. 안전하게 비중을 늘리세요.")
elif curr < limit:
    st.warning(f"### 🟡 '적립식 대응' 구간\n평균을 넘었습니다. 목돈 투입은 자제하고 소액 적립식으로만 대응하세요.")
else:
    st.error(f"### 🚨 '매수 금지' 구간\n과열권입니다. 지금 사면 물립니다. 현금 들고 기다리세요.")

st.caption(f"📅 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
