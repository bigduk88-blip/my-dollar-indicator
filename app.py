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
        # 넉넉하게 데이터를 가져와서 처리
        data = yf.download(ticker, period="3y")
        if data.empty:
            raise ValueError("데이터를 가져올 수 없습니다.")
        
        # 최신 환율 및 3년 평균 계산
        curr = round(float(data['Close'].iloc[-1]), 2)
        avg = round(float(data['Close'].mean()), 2)
        # 매수 한계 (박종훈 기자 기준: 평균 + 7%)
        limit = round(avg * 1.07, 2)
        return curr, avg, limit
    except Exception as e:
        st.error(f"환율 데이터를 가져오는 중 오류가 발생했습니다: {e}")
        # 오류 발생 시 임시 기본값 반환 (앱 중단 방지)
        return 1400.00, 1350.00, 1444.50

# 데이터 불러오기
curr, avg, limit = get_data()

# ==========================================
# 2. 게이지 디자인 (바늘 3개 구현 핵심 로직)
# ==========================================

fig = go.Figure()

# 게이지 표시 범위 설정 (동적으로 보기 좋게 조정)
min_scale = avg * 0.85
max_scale = avg * 1.15

# 2-1. 기본 게이지 배경 그리기 (바늘 없이 배경 색상띠만)
fig.add_trace(go.Indicator(
    mode = "gauge", 
    value = curr,   # 실제 바늘은 아래에서 따로 그립니다.
    gauge = {
        'shape': "angular",
        # 눈금 표시 (범위 설정)
        'axis': {'range': [min_scale, max_scale], 'tickwidth': 2, 'tickcolor': "#333", 'tickfont': {'size': 14}},
        'bar': {'color': "rgba(0,0,0,0)"}, # 기본 바늘 숨김
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "#eee",
        'steps': [
            # 형님 요청대로 빈틈없이 색상 연결
            {'range': [min_scale, avg], 'color': "#00E676"},   # 초록 (안전)
            {'range': [avg, limit], 'color': "#FFD600"},       # 노랑 (주의)
            {'range': [limit, max_scale], 'color': "#FF5252"}] # 빨강 (위험) - limit부터 바로 시작
    }
))

# 2-2. 바늘 좌표 계산 함수 (오류 수정 및 안정화)
def get_arrow_coords(value, min_v, max_v):
    # 값을 범위 내 비율(0~1)로 변환
    try:
        ratio = (value - min_v) / (max_v - min_v)
        ratio = max(0.0, min(1.0, ratio)) # 범위 밖 값 안전장치
    except ZeroDivisionError:
        ratio = 0.5 # 만약 범위 계산 오류 시 중앙에 위치

    # 각도 계산 (왼쪽 180도 -> 오른쪽 0도)
    angle_deg = 180 - (ratio * 180)
    angle_rad = math.radians(angle_deg)
    
    # 게이지 중심점 및 바늘 길이 설정
    center_x, center_y = 0.5, 0.25 # 종이 좌표 기준 중심
    radius = 0.45 # 바늘 길이

    # 끝점 좌표 계산 (삼각함수)
    tip_x = center_x + radius * math.cos(angle_rad)
    tip_y = center_y + radius * math.sin(angle_rad)
    
    return tip_x, tip_y, angle_deg

# 2-3. 바늘 3개 그리기

# (1) 3년 평균 바늘 (초록색)
ax, ay, _ = get_arrow_coords(avg, min_scale, max_scale)
fig.add_annotation(x=ax, y=ay, ax=0.5, ay=0.25, xref='paper', yref='paper', axref='paper', ayref='paper',
                   showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor='green', opacity=0.6)
fig.add_annotation(x=ax, y=ay, text=f"3년평균<br>{avg:,}", font=dict(color="green", size=12), showarrow=False, yshift=20)

# (2) 매수 한계 바늘 (빨간색)
lx, ly, _ = get_arrow_coords(limit, min_scale, max_scale)
fig.add_annotation(x=lx, y=ly, ax=0.5, ay=0.25, xref='paper', yref='paper', axref='paper', ayref='paper',
                   showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor='red', opacity=0.6)
fig.add_annotation(x=lx, y=ly, text=f"매수한계<br>{limit:,}", font=dict(color="red", size=12), showarrow=False, yshift=20)

# (3) 현재가 바늘 (검정색, 가장 두껍고 진하게)
cx, cy, _ = get_arrow_coords(curr, min_scale, max_scale)
fig.add_annotation(x=cx, y=cy, ax=0.5, ay=0.25, xref='paper', yref='paper', axref='paper', ayref='paper',
                   showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=5, arrowcolor='black')

# 레이아웃 및 현재가 텍스트 표시
fig.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=30, b=20),
    paper_bgcolor = "rgba(0,0,0,0)",
    font={'family': "Arial, sans-serif"},
    # 현재가 중앙 하단 표시 (가장 중요!)
    annotations=[dict(x=0.5, y=0, text=f"현재가: <b>{curr:,}원</b>", font=dict(color="black", size=35), showarrow=False, xref='paper', yref='paper', yshift=-10)]
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. 하단 가이드 및 조언
# ==========================================

st.markdown("### 📊 구간별 투자 가이드")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**🟢 안전 (평균 이하)**\n\n기계적 매수 구간")
with col2:
    st.markdown(f"**🟡 주의 (7% 이내)**\n\n소액 적립만 권장")
with col3:
    st.markdown(f"**🔴 위험 (7% 초과)**\n\n매수 중단, 관망")

st.markdown("---")

# 박종훈 기자 조언
if curr < avg:
    st.success(f"### ✅ '적극 매수' 구간입니다.\n**박종훈 기자의 조언:** \"환율이 평균({avg:,}원) 아래일 때가 가장 안전합니다. 공포를 이기고 달러 자산을 모아가세요.\"")
elif curr < limit:
    st.warning(f"### 🟡 '적립식 대응' 구간입니다.\n**박종훈 기자의 조언:** \"평균을 넘었습니다. 조급하다면 목돈 투입 대신 정해진 날짜에 소액 적립식으로만 대응하세요.\"")
else:
    st.error(f"### 🚨 '매수 금지' 구간입니다.\n**박종훈 기자의 조언:** \"과열권입니다. 지금 사면 상투를 잡을 수 있습니다. 현금을 쥐고 인내하며 기회를 기다리세요.\"")

st.caption(f"📅 데이터 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (최근 3년 기준)")
