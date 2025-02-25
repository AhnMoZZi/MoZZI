import streamlit as st
import openai
import os
import yfinance as yf
import matplotlib.pyplot as plt
import sentry_sdk

# 🔹 Sentry 초기화 (실시간 오류 감지)
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0
)

# 🔹 환경 변수에서 OpenAI API 키 가져오기 (예외 처리 추가!)
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("🔴 ERROR: OpenAI API Key가 설정되지 않았습니다! Streamlit Secrets에서 설정을 확인하세요.")
    st.stop()

# 🔹 OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY  # ✅ 최신 방식 적용

# 🔹 GitHub Actions에서 오류 발생 시 자동 Issue 생성 (GitHub API 활용)
def create_github_issue(error_message):
    import requests

    GITHUB_REPO = "YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    if not GITHUB_TOKEN:
        print("GitHub Token이 설정되지 않았습니다.")
        return

    issue_title = "⚠ Streamlit 앱 오류 발생"
    issue_body = f"### 오류 내용\n```\n{error_message}\n```"

    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"title": issue_title, "body": issue_body}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("✅ GitHub Issue가 성공적으로 생성되었습니다.")
    else:
        print("❌ GitHub Issue 생성 실패:", response.json())

# 🔹 금 / 환율 / 비트코인 실시간 데이터 가져오기
def get_market_data(symbol):
    try:
        data = yf.download(symbol, period="7d", interval="1d")
        return data
    except Exception as e:
        st.error(f"🔴 데이터 가져오기 실패: {e}")
        create_github_issue(str(e))
        sentry_sdk.capture_exception(e)
        return None

# 🔹 AI를 활용한 가격 예측
def predict_price(trend_data, asset_name):
    try:
        prompt = f"Here is the price trend for {asset_name}:\n\n{trend_data}\n\nBased on this trend, will the price go up or down tomorrow?"
        
        response = openai.ChatCompletion.create(  # ✅ 최신 OpenAI 방식 적용!
            model="gpt-4o",  # ✅ 모델을 `gpt-4o`로 변경!
            messages=[{"role": "system", "content": "You are a financial analyst."},
                      {"role": "user", "content": prompt}]
        )

        return response["choices"][0]["message"]["content"]
    
    except Exception as e:
        st.error(f"🔴 AI 예측 실패: {e}")
        create_github_issue(str(e))
        sentry_sdk.capture_exception(e)
        return "❌ 예측 실패"

# 🔹 Streamlit UI 설정
st.title("📈 AI 기반 가격 예측 앱")
st.write("금 / 환율 / 비트코인 가격을 AI가 예측해줍니다.")

# 🔹 사용자 선택: 금, 달러 환율, 비트코인
option = st.selectbox("자산을 선택하세요:", ["Gold (GC=F)", "USD/KRW (KRW=X)", "Bitcoin (BTC-USD)"])

# 🔹 선택한 자산 데이터 가져오기
data = get_market_data(option)
if data is not None:
    st.subheader(f"{option} 최근 7일 가격 변동")
    st.line_chart(data["Close"])

    # 🔹 AI 예측 실행
    st.subheader("📊 AI 예측 결과")
    trend_data = data["Close"].to_string()
    prediction = predict_price(trend_data, option)
    st.write(f"🔮 **AI 분석:** {prediction}")

