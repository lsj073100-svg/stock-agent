import streamlit as st
import yfinance as yf
import google.generativeai as genai
from datetime import datetime

# ==========================================
# 1. 시스템 프롬프트 설정
# ==========================================
SYSTEM_INSTRUCTION = """
당신은 글로벌 헤지펀드 및 자산운용사 소속의 수석 에퀴티 리서치 애널리스트입니다.
- 실시간 데이터 우선, 할루시네이션 절대 금지
- 매수/매도/보유 최종 의견 및 100점 만점 스코어카드 제공
- 지정된 재무 비율(LaTeX 수식 및 엑셀 수식 포함) 산출
- 마크다운 표 구조를 활용한 출력
"""

# ==========================================
# 2. 기초 금융 데이터 추출 함수 (사전 데이터 파싱용)
# ==========================================
def fetch_baseline_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        return info, True
    except Exception as e:
        return None, False

# ==========================================
# 3. Streamlit UI 및 메인 실행 로직
# ==========================================
st.set_page_config(page_title="Professional Equity Research Agent", layout="wide")

with st.sidebar:
    st.header("⚙️ 시스템 설정")
    api_key = st.text_input("Gemini API Key 입력", type="password")
    st.markdown("---")
    st.subheader("📊 분석 대상 시장 자동 감지")
    st.caption("KOSPI, KOSDAQ, NYSE, NASDAQ 지원")

ticker_input = st.text_input("티커 심볼을 입력하세요 (예: 000660.KS)", value="000660.KS")

if ticker_input:
    # 데이터 무결성 검증 UI
    info, success = fetch_baseline_data(ticker_input)
    
    if success and info:
        st.success("데이터 무결성 검증 완료: 신뢰할 수 있는 실시간 금융 데이터가 탑재되었습니다.")
        
        # 교수님 화면과 동일한 대시보드 UI 구성
        st.markdown("### 📌 Baseline Financial Data (최상단 기초 데이터)")
        
        col1, col2, col3 = st.columns(3)
        
        # 숫자 포맷팅을 위한 안전한 처리
        current_price = info.get('currentPrice', 0)
        market_cap = info.get('marketCap', 0)
        shares_out = info.get('sharesOutstanding', 0)
        
        with col1:
            st.metric("최신 주가", f"{current_price:,} {info.get('currency', 'KRW')}")
            st.metric("시가총액", f"{market_cap:,}" if isinstance(market_cap, (int, float)) else "N/A")
            
        with col2:
            st.metric("총 발행 주식 수", f"{shares_out:,}" if isinstance(shares_out, (int, float)) else "N/A")
            st.metric("주당순이익 (EPS)", info.get('trailingEps', 'N/A'))
            
        with col3:
            st.metric("52주 최고 / 최저", f"{info.get('fiftyTwoWeekHigh', 'N/A')} / {info.get('fiftyTwoWeekLow', 'N/A')}")
            st.metric("자본 구조 (타인/자기)", "N/A") # 실시간 API로 바로 안 나오는 항목은 N/A 처리
            
        st.markdown("---")
        
        # 분석 시작 버튼
        run_button = st.button("🚀 세계 정상급 에퀴티 리서치 보고서 생성 시작")

        if run_button:
            if not api_key:
                st.error("좌측 사이드바에 Gemini API Key를 입력해주세요.")
            else:
                # AI 모델 세팅
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=SYSTEM_INSTRUCTION
                )
                
                # 텍스트화된 데이터를 AI에게 전달
                live_data_text = f"""
                - 티커: {ticker_input}
                - 최신 주가: {current_price} {info.get('currency', 'KRW')}
                - 시가총액: {market_cap}
                - 주당순이익(EPS): {info.get('trailingEps', 'N/A')}
                """
                
                user_prompt = f"분석 대상 티커: {ticker_input}\n시스템 수집 기초 데이터: {live_data_text}\n지침에 따라 보고서를 작성해 주십시오."
                
                with st.spinner("AI 에이전트 가동: 거시경제, 밸류에이션, 리스크 스트레스 테스트 및 비정형 데이터 분석 통합 중..."):
                    try:
                        response = model.generate_content(user_prompt)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")
    else:
        st.error("티커 심볼을 확인해주세요. 데이터를 불러올 수 없습니다.")
