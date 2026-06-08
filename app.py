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
# 2. 기초 금융 데이터 추출 함수
# ==========================================
def fetch_baseline_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        baseline_data = f"""
        [실시간 기초 데이터 검증]
        - 티커: {ticker_symbol}
        - 최신 주가: {info.get('currentPrice', 'N/A')} {info.get('currency', 'USD')}
        - 시가총액: {info.get('marketCap', 'N/A')}
        - 총 발행 주식 수: {info.get('sharesOutstanding', 'N/A')}
        - 주당순이익(EPS): {info.get('trailingEps', 'N/A')}
        - 52주 최고가: {info.get('fiftyTwoWeekHigh', 'N/A')}
        - 52주 최저가: {info.get('fiftyTwoWeekLow', 'N/A')}
        - 최근 10일 평균 거래량: {info.get('averageDailyVolume10Day', 'N/A')}
        - 업종(Industry): {info.get('industry', 'N/A')}
        """
        return baseline_data, True
    except Exception as e:
        return f"데이터 추출 실패 (Error: {e})", False

# ==========================================
# 3. Streamlit UI 및 메인 실행 로직
# ==========================================
st.set_page_config(page_title="Professional Equity Research Agent", layout="wide")

st.title("📈 AI 에퀴티 리서치 에이전트")
st.markdown("글로벌 헤지펀드 수준의 종목 분석 보고서를 자동으로 생성합니다.")

with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key", type="password", help="Google AI Studio에서 발급받은 API 키를 입력하세요.")
    st.markdown("---")
    ticker_input = st.text_input("티커 심볼 (예: AAPL, 005930.KS)", value="AAPL")
    run_button = st.button("🚀 분석 시작", use_container_width=True)

if run_button:
    if not api_key:
        st.error("Gemini API Key를 입력해주세요.")
    elif not ticker_input:
        st.error("분석할 티커 심볼을 입력해주세요.")
    else:
        st.info(f"**{ticker_input}** 실시간 데이터 수집 및 분석을 시작합니다. (약 30초~1분 소요)")
        
        # 1. API 설정
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        with st.spinner("야후 파이낸스(Yahoo Finance)에서 기초 데이터를 수집 중입니다..."):
            live_data, success = fetch_baseline_data(ticker_input)
            
        if success:
            st.success("기초 데이터 수집 완료! AI 분석을 진행합니다.")
            
            user_prompt = f"""
            분석 대상 티커: {ticker_input}
            
            시스템에 수집된 실시간 기초 데이터는 다음과 같습니다:
            {live_data}
            
            위 데이터를 바탕으로, 지침에 명시된 전 과정을 수행하여 '종합 주식 평가 보고서(Comprehensive Equity Research Report)'를 작성해 주십시오.
            """
            
            with st.spinner("Gemini가 수석 애널리스트 모드로 보고서를 작성 중입니다..."):
                try:
                    response = model.generate_content(user_prompt)
                    
                    st.markdown("---")
                    st.subheader(f"📊 {ticker_input} 종합 주식 평가 보고서")
                    st.markdown(response.text)
                    
                    # 다운로드 버튼 제공
                    date_str = datetime.now().strftime("%Y%m%d")
                    st.download_button(
                        label="📥 보고서 마크다운(.md) 파일 다운로드",
                        data=response.text,
                        file_name=f"Equity_Research_Report_{ticker_input}_{date_str}.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"AI 리포트 생성 중 오류가 발생했습니다: {e}")
        else:
            st.error(live_data)
