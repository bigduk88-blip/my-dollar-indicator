import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="박종훈의 달러 신호등", layout="centered")

# 2. CSS 스타일 (가독성 보강 및 인터랙션 최적화)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
        html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
        
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 500px;
        }
        
        .element-container { margin-bottom: 0px !important; }
        
        .current-price-label { font-size: 1rem; color: #666; margin-bottom: -5px; text-align: center; }
        .current-price-value { font-size: 2.8rem; font-weight: 900; color: #333; text-align: center; line-height: 1.1; }
        
        .signal-container {
            display: flex;
            justify-content: space-between;
            gap: 8px;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        
        /* 기본 신호등 스타일 (비활성 상태 가독성 향상) */
        .signal-box {
            flex: 1;
            padding: 12px 2px;
            border-radius: 12px;
            text-align: center;
            color: white;
            opacity: 0.45; /* 흐림 정도 완화 (정보 확인 용이) */
            transition: all 0.3s ease;
            transform: scale(0.92); /* 비활성은 약간 작게 */
        }
        
        .signal-title { font-size: 0.9rem; font-weight: 700; margin-bottom: 2px; }
        .signal-desc { font-size: 0.75rem; font-weight: 400; }
        .signal-price { font-size: 0.8rem; font-weight: 700; margin-top: 4px; background: rgba(0,0,0,0.15); padding: 2px 4px; border-radius: 4px; display: inline-block;}

        /* 활성화 상태 (크게 강조 및 뚜렷하게) */
        .active {
            opacity: 1.0 !important;
            transform: scale(1.1) !important; /* 크기 확대 */
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            border: 2.5px solid #fff;
            z-index: 10;
        }

        .advice-container {
            padding: 15px;
            border-radius: 10px;
            margin-top: 5px;
            border-left: 5px solid;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
        return 1447.0, 1370.3, 1466.2

curr, avg, limit = get_data()

# 4. 상태 판단 로직
if curr <= avg:
    status, title, msg = "GREEN", "✅ 적극 매수 구간", f"환율이 3년 평균({avg:,.1f}원)보다 저렴합니다.<br>지금이 가장 안전한 기회입니다."
    bg, border, text = "#e8f5e9", "#27ae60", "#1b5e20"
elif curr <= limit:
    status, title, msg = "YELLOW", "🟡 적립식 대응 구간", f"평균을 넘었지만 아직 과열권({limit:,.1f}원)은 아닙니다.<br>소액 적립식 환전을 권장합니다."
    bg, border, text = "#fffde7", "#f1c40f", "#827717"
else:
    status, title, msg = "RED", "🚨 매수 금지 구간", f"현재 환율은 3년 평균 대비 7% 이상 비싼 상태입니다.<br>인내하며 다음 기회를 기다리세요."
    bg, border, text = "#ffebee", "#e74c3c", "#b71c1c"

# 5. 화면 구성
st.markdown(f'<div class="current-price-label">실시간 달러 환율</div><div class="current-price-value">{curr:,.0f}<span style="font-size:1.2rem;">원</span></div>', unsafe_allow_html=True)

c_green = "active" if status == "GREEN" else ""
c_yellow = "active" if status == "YELLOW" else ""
c_red = "active" if status == "RED" else ""

st.markdown(f"""
    <div class="signal-container">
        <div class="signal-box {c_green}" style="background-color: #27ae60;">
            <div class="signal-title">🟢 매수</div><div class="signal-desc">평균이하</div><div class="signal-price">~{avg:,.0f}</div>
        </div>
        <div class="signal-box {c_yellow}" style="background-color: #f1c40f; color: #333;">
            <div class="signal-title">🟡 주의</div><div class="signal-desc">7%이내</div><div class="signal-price">~{limit:,.0f}</div>
        </div>
        <div class="signal-box {c_red}" style="background-color: #e74c3c;">
            <div class="signal-title">🔴 금지</div><div class="signal-desc">과열</div><div class="signal-price">{limit:,.0f}~</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="advice-container" style="background-color: {bg}; border-left-color: {border}; color: {text};"><h4 style="margin-top:0; color:{text}; font-size:1rem;">{title}</h4><p style="font-size:0.92rem; line-height:1.5; margin-bottom:0;">{msg}</p></div>', unsafe_allow_html=True)

# 6. 하단 정보
st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1: st.write(f"📉 3년 평균: **{avg:,.1f}원**")
with col2: st.write(f"🛑 매수 한계: **{limit:,.1f}원**")

st.caption(f"📅 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
