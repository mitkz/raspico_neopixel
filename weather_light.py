# 天気に応じてNeoPixelの色を変えるプログラム

# 必要なライブラリをインポートする
import network        # Wi-Fi接続用
import urequests     # インターネットからデータを取得するため
import json          # JSONデータを処理するため
import time          # 待ち時間を入れるため
import machine       # ハードウェア制御用
import neopixel      # NeoPixel（LED）操作用

# Wi-Fiの設定を書く
SSID = 'yourSSID'         # Wi-Fiのネットワーク名
PASSWORD = 'yourpassword'  # Wi-Fiのパスワード

# OpenWeatherMap APIキー
API_KEY = "yourAPIkey"  # ここにあなたのAPIキーを設定してください

# NeoPixelの設定
NUM_LEDS = 7        # LEDの数
PIN_NUM = 27        # LEDが接続されているピン番号
pin = machine.Pin(PIN_NUM)
np = neopixel.NeoPixel(pin, NUM_LEDS)

# 天気に対応する色の設定
WEATHER_COLORS = {
    'Clear': (0, 0, 255),       # 晴れ: 青色
    'Clouds': (100, 100, 100),  # 曇り: 灰色
    'Rain': (0, 0, 150),        # 雨: 暗い青
    'Thunderstorm': (255, 255, 0),  # 雷雨: 黄色
    'Drizzle': (0, 100, 255),   # 小雨: 薄い青
    'Snow': (255, 255, 255),    # 雪: 白色
    'Mist': (50, 50, 50),       # 霧: 薄い灰色
    'default': (0, 255, 0)      # その他の天気: 緑色
}

# 気象情報取得用のAPI URL（OpenWeatherMap）
# 名護市の緯度経度を使用
WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?lat=26.5914&lon=127.9773&appid={API_KEY}"


# Wi-Fiに接続する関数
def connect_wifi():
    print("Connecting to Wi-Fi...")
    wlan = network.WLAN(network.STA_IF)  # Wi-Fiインターフェースを作る
    wlan.active(True)                   # Wi-Fiを有効にする
    wlan.connect(SSID, PASSWORD)         # 指定したSSIDとパスワードで接続する

    # Wi-Fi接続が完了するまで待つ
    while not wlan.isconnected():
        print("Connecting...")
        time.sleep(1)

    # 接続成功したらIPアドレスを表示
    print("Wi-Fi connected! IP:", wlan.ifconfig()[0])
    return wlan


# 天気情報を取得する関数
def get_weather():
    try:
        # APIからデータを取得する
        print("Fetching weather data...")
        response = urequests.get(WEATHER_URL)
        data = json.loads(response.text)
        response.close()  # 接続を閉じる

        # 天気情報を取り出す
        weather = data["weather"][0]["main"]
        description = data["weather"][0]["description"]
        temp = data["main"]["temp"] - 273.15  # ケルビンから摂氏に変換

        print(f"Nago City weather: {weather}, details: {description}, temperature: {temp:.1f}degrees Celsius")
        return weather

    except Exception as e:
        print("Error:", e)
        return "default"  # エラーが発生した場合はデフォルト値を返す


# LEDの色を設定する関数
def set_led_color(weather):
    # 天気に対応する色を取得（存在しない場合はデフォルト色を使用）
    color = WEATHER_COLORS.get(weather, WEATHER_COLORS["default"])
    print(f"Weather: {weather} → LED color: RGB{color}")

    # すべてのLEDを同じ色に設定
    for i in range(NUM_LEDS):
        np[i] = color
    np.write()  # LEDに反映する


# メイン処理
def main():
    # Wi-Fiに接続
    connect_wifi()

    print("Changing LED colors based on Nago City weather")

    try:
        while True:
            # 天気を取得
            weather = get_weather()

            # LEDの色を設定
            set_led_color(weather)

            # 10分間待機（天気情報を頻繁に取得しすぎないため）
            print("Waiting for 10 minuites ...")
            time.sleep(600)  # 600秒（10分）待機

    except KeyboardInterrupt:
        # プログラムが中断された場合（Ctrl+C）
        print("Program terminated")
        # LEDを消灯させる
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 0)
        np.write()


# プログラムを実行
if __name__ == "__main__":
    main()
