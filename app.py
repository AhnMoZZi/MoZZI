import streamlit as st
import openai
import os
import yfinance as yf
import matplotlib.pyplot as plt

# 🔹 환경 변수에서 OpenAI API 키 가져오기 (예외 처리 추가!)
if "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
else:
    st.error("🔴 ERROR: OpenAI API Key가 설정되지 않았습니다! Streamlit Secrets에서 설정을 확인하세요.")
    st.stop()

# 🔹 OpenAI 클라이언트 생성 (최신 API 방식 적용)
client = openai.OpenAI(api_key=OPENAI_API_KEY)  # ✅ 최신 방식 적용

# 🔹 금 / 환율 / 비트코인 실시간 데이터 가져오기
def get_market_data(symbol):
    data = yf.download(symbol, period="7d", interval="1d")
    return data

# 🔹 AI를 활용한 가격 예측
def predict_price(trend_data, asset_name):
    prompt = f"Here is the price trend for {asset_name}:\n\n{trend_data}\n\nBased on this trend, will the price go up or down tomorrow?"
    
    response = client.chat.completions.create(  # ✅ 최신 OpenAI 방식 적용!
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a financial analyst."},
                  {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content  # ✅ 최신 방식으로 응답 가져오기

# 🔹 Streamlit UI 설정
st.title("📈 AI 기반 가격 예측 앱")
st.write("금 / 환율 / 비트코인 가격을 AI가 예측해줍니다.")

# 🔹 사용자 선택: 금, 달러 환율, 비트코인
option = st.selectbox("자산을 선택하세요:", ["Gold (GC=F)", "USD/KRW (KRW=X)", "Bitcoin (BTC-USD)"])

# 🔹 선택한 자산 데이터 가져오기
data = get_market_data(option)
st.subheader(f"{option} 최근 7일 가격 변동")
st.line_chart(data["Close"])

# 🔹 AI 예측 실행
st.subheader("📊 AI 예측 결과")
trend_data = data["Close"].to_string()
prediction = predict_price(trend_data, option)
st.write(f"🔮 **AI 분석:** {prediction}")
