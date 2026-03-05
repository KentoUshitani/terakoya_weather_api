import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
import os
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()

# ==========================================
# 関数: 取得したデータから画面（カードとグラフ）を描画する
# ==========================================
def show_weather_card(weather_json, city_name):
    try:
        # OpenWeatherMapのJSONから現在のデータを抽出
        current = weather_json["list"][0]
        temp = round(current["main"]["temp"], 1) # 気温(℃)を小数第1位に丸める
        desc = current["weather"][0]["description"] # 天気の状態
        icon_code = current["weather"][0]["icon"]

        # アイコンと背景色の判定
        icon, bg_grad = "☁️", "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
        if "01" in icon_code: icon, bg_grad = "☀️", "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        if "02" in icon_code or "03" in icon_code or "04" in icon_code: icon, bg_grad = "☁️", "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
        if "09" in icon_code or "10" in icon_code: icon, bg_grad = "☔", "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        if "11" in icon_code: icon, bg_grad = "⚡", "linear-gradient(135deg, #434343 0%, #000000 100%)"
        if "13" in icon_code: icon, bg_grad = "☃️", "linear-gradient(135deg, #e6e9f0 0%, #eef1f5 100%)"

        # HTMLを使ったお天気カードの描画
        card_html = f"""
        <div style="width: 100%; padding: 20px; border-radius: 15px; background: {bg_grad}; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2); margin-bottom: 20px;">
            <div style="font-size: 1.2rem; opacity: 0.9;">📍 {city_name}</div>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 4rem;">{icon}</div>
                <div style="text-align: right;">
                    <div style="font-size: 3.5rem; font-weight: bold;">{temp}℃</div>
                    <div style="font-size: 1rem;">{desc}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        # グラフの描画 (今後24時間 = 3時間毎×8個のデータ)
        forecast_list = weather_json["list"][:8]
        times = [item["dt_txt"][11:16] for item in forecast_list] # 時刻 "12:00" を抽出
        temps = [item["main"]["temp"] for item in forecast_list]

        df = pd.DataFrame({"時刻": times, "気温": temps})
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df["時刻"], df["気温"], marker="o", color="#007bff", linewidth=2)
        ax.set_title(f"今後の気温推移 ({city_name})")
        ax.grid(True, linestyle="--", alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"データ解析エラー: {e}")

# ==========================================
# メイン処理 (画面の組み立てとAPI通信)
# ==========================================
def main():
    st.set_page_config(page_title="Weather App", page_icon="🌤️")
    st.title("🌤️ 天気予報アプリハンズオン")
    
    # 検索窓
    city = st.text_input("都市名を入力してください（日本語OK）", "東京都")

    if st.button("天気を調べる"):
        
        # 1. 接続先URL
        url = "https://api.openweathermap.org/data/2.5/forecast"

        # 2. 環境変数からAPIキーを取得
        api_key = os.getenv("OPENWEATHER_API_KEY")

        if not api_key:
            st.error(".env ファイルに OPENWEATHER_API_KEY が設定されていません。")
            return

        # パラメータの設定
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "ja"
        }

        # 3. データ取得
        res = requests.get(url, params=params)

        # 結果の判定と表示
        if res.status_code == 200:
            data = res.json()
            actual_city_name = data["city"]["name"]
            st.success(f"発見: {actual_city_name} のデータを取得しました！")
            # 修正ポイント: 閉じカッコを補完しました
            show_weather_card(data, actual_city_name)
            
        elif res.status_code == 401:
            st.error("エラー (401): APIキーが無効、または有効化待ちです。")
            
        elif res.status_code == 404:
            st.error("エラー (404): その都市は見つかりませんでした。別の書き方を試してください。")
            
        else:
            st.error(f"通信エラーが発生しました (コード: {res.status_code})。")

if __name__ == "__main__":
    main()