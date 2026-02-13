import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="박종훈의 달러 신호등", layout="centered")

# 2. CSS 스타일 (신호등 효과, 폰트 및 조언 박스)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
        html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
        
        /* 현재가 스타일 */
        .current-price-label { font-size: 1.2rem; color: #666; margin-bottom: -10px; text-align: center; }
        .current-price-value { font-size: 3.5rem; font-weight: 900; color: #333; text-align: center; line-height: 1.2; }
        
        /* 신호등 박스 스타일 */
        .signal-container {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .signal-box {
            flex: 1;
            padding: 15px 5px;
            border-radius: 15px;
            text-align: center;
            color: white;
            opacity: 0.2; /* 기본은 흐리게 */
            transition: all 0.3s ease;
        }
        .signal-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 5px; }
        .signal-desc { font-size: 0.8rem; font-weight: 400; }
        .signal-price { font-size: 0.9rem; font-weight: 700; margin-top: 5px; background: rgba(0,0,0,0.2); padding: 2px 5px; border-radius: 5px; display: inline-block;}

        /* 활성화 상태 (불 켜짐) */
        .active {
            opacity: 1.0 !important;
            transform: scale(1.05);
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
            border: 2px solid white;
        }

        /* 조언 메시지 박스 스타일 */
        .advice-container {
            padding: 20px;
            border-radius: 12px;
            margin-top: 10px;
            border-left: 6px solid;
        }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터 로딩
@st.cache_data(ttl=86400)
def get_data():
    try:
        ticker = "USDKRW=X"
        data = yf.download(ticker, period="3y")
        curr = round(float(data['Close'].iloc[-1]), 2)
        avg = round(float(data['Close'].mean()), 2)
        limit = round(avg * 1.07, 2)
        return curr, avg, limit
    except:
        return 1400.0, 1350.0, 1444.5

curr, avg, limit = get_data()

# 4. 상태 판단 로직 및 스타일 설정
if curr <= avg:
    status = "GREEN"
    advice_title = "✅ 적극 매수 구간"
    advice_msg = f"현재 환율이 3년 평균({avg:,.0f}원)보다 저렴합니다.<br>지금이 가장 안전한 기회입니다. 기계적으로 달러를 모으세요."
    bg_color, border_color, text_color = "#e8f5e9", "#27ae60", "#1b5e20"
elif curr <= limit:
    status = "YELLOW"
    advice_title = "🟡 적립식 대응 구간"
    advice_msg = f"평균을 넘었지만 아직 과열권({limit:,.0f}원)은 아닙니다.<br>목돈 투입은 자제하고, 매달 정해진 날에 소액만 환전하세요."
    bg_color, border_color, text_color = "#fffde7", "#f1c40f", "#827717"
else:
    status = "RED"
    advice_title = "🚨 매수 금지 구간"
    advice_msg = f"현재 환율은 3년 평균 대비 7% 이상 비싼 과열 상태입니다.<br>지금 사면 상투입니다. 현금을 쥐고 인내하십시오."
    bg_color, border_color, text_color = "#ffebee", "#e74c3c", "#b71c1c"

# 5. 화면 구성

# (1) 현재가 표시
st.markdown(f"""
    <div class="current-price-label">실시간 달러 환율</div>
    <div class="current-price-value">{curr:,.0f}<span style="font-size:1.5rem; font-weight:400;">원</span></div>
""", unsafe_allow_html=True)

# (2) 신호등 UI
c_green = "active" if status == "GREEN" else ""
c_yellow = "active" if status == "YELLOW" else ""
c_red = "active" if status == "RED" else ""

st.markdown(f"""
    <div class="signal-container">
        <div class="signal-box {c_green}" style="background-color: #27ae60;">
            <div class="signal-title">🟢 적극 매수</div>
            <div class="signal-desc">평균 이하</div>
            <div class="signal-price">~ {avg:,.0f}원</div>
        </div>
        <div class="signal-box {c_yellow}" style="background-color: #f1c40f; color: #333;">
            <div class="signal-title">🟡 분할 매수</div>
            <div class="signal-desc">7% 이내</div>
            <div class="signal-price">{avg:,.0f} ~ {limit:,.0f}원</div>
        </div>
        <div class="signal-box {c_red}" style="background-color: #e74c3c;">
            <div class="signal-title">🔴 매수 금지</div>
            <div class="signal-desc">7% 초과</div>
            <div class="signal-price">{limit:,.0f}원 ~</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# (3) 핵심 조언 박스 (수정 포인트: HTML 렌더링으로 코드 노출 해결)
st.markdown(f"""
    <div class="advice-container" style="background-color: {bg_color}; border-left-color: {border_color}; color: {text_color};">
        <h3 style="margin-top: 0; color: {text_color};">{advice_title}</h3>
        <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 0;">{advice_msg}</p>
    </div>
""", unsafe_allow_html=True)

# (4) 하단 세부 수치
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**📉 3년 평균 환율**\n\n### {avg:,.2f}원")
with col2:
    st.markdown(f"**🛑 매수 한계선 (+7%)**\n\n### {limit:,.2f}원")

st.caption(f"📅 데이터 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} (출처: Yahoo Finance)")
