# 必要なライブラリをインポートする
import network        # Wi-Fi接続用
import socket         # ネットワーク通信（Webサーバ）用
import machine        # ハードウェア制御（ピン操作）用
import neopixel       # NeoPixel（LED）操作用
import ure            # URLの中の文字を取り出すための簡単な正規表現ライブラリ

# Wi-Fiの設定を書く
SSID = 'yourSSID'         # Wi-Fiのネットワーク名
PASSWORD = 'yourpassword'  # Wi-Fiのパスワード

# NeoPixel（LED）の設定を書く
NUM_LEDS = 7        # LEDの数（24個）
PIN_NUM = 27          # ピン番号（GPIO0）に接続している
pin = machine.Pin(PIN_NUM)             # ピンを初期化する
np = neopixel.NeoPixel(pin, NUM_LEDS)   # NeoPixelを初期化する

# Wi-Fiに接続する
wlan = network.WLAN(network.STA_IF)   # Wi-Fiインターフェースを作る
wlan.active(True)                    # Wi-Fiを有効にする
wlan.connect(SSID, PASSWORD)          # 指定したSSIDとパスワードで接続する

# Wi-Fi接続が完了するまで待つ
while not wlan.isconnected():
    pass  # まだなら何もせず待つ

# Wi-Fi接続に成功したらIPアドレスなどを表示する
print('Connected to AP! Interface info ->', wlan.ifconfig())


# HTMLファイル(index.html)を読み込む関数を作る
def load_html():
    with open('index.html', 'r') as f:  # index.htmlファイルを開く
        return f.read()                 # ファイルの中身を読み込んで返す


# Webサーバ用のソケットを作る
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]  # IPアドレスとポート番号（80番）を指定
s = socket.socket()      # ソケットを作成する
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ソケットを再利用可能にする
s.bind(addr)             # 指定したアドレスとポートにソケットを結びつける
s.listen(1)              # 接続を1つ受け付ける設定にする

print('starting web server...')

# 無限ループでサーバを動かし続ける
while True:
    cl, addr = s.accept()        # クライアント（スマホやPC）から接続を受け付ける
    print('client connected', addr)  # 接続してきた機器の情報を表示する
    request = cl.recv(1024)       # クライアントから送られてきたデータを受け取る
    request = request.decode('utf-8')  # データ（バイト型）を文字列に変換する

    # URLの中からr,g,bの値を探す
    match = ure.search(r'r=(\d+)&g=(\d+)&b=(\d+)', request)
    if match:
        # r, g, bの値が見つかったら、それぞれ取り出して整数に変換する
        r = int(match.group(1))
        g = int(match.group(2))
        b = int(match.group(3))
        print(f'renew RGB: ({r}, {g}, {b})')  # 新しいRGB値を表示する

        # 全てのLEDを新しい色で光らせる
        for i in range(NUM_LEDS):
            np[i] = (r, g, b)  # i番目のLEDに色をセットする
        np.write()  # まとめてLEDに反映する

    # クライアントにHTMLページを送る
    response = load_html()  # HTMLファイルを読み込む
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')  # HTTPヘッダを送る
    cl.send(response)  # HTMLの中身を送る
    cl.close()  # クライアントとの通信を終了する
