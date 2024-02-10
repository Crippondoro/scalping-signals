import yfinance as yf
from tkinter import *
from tkinter import filedialog
from telegram import Bot
import threading
import time
from datetime import datetime
from collections import defaultdict

TELEGRAM_BOT_TOKEN = "YUOR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = YOUR_CHAT_ID

prev_status_dict = {}
last_message_time = 0
lock = threading.Lock()

telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_telegram_message(message):
    try:
        telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def calculate_rsi(close_prices, window_length=14):
    price_diff = close_prices.diff(1)
    gains = price_diff.where(price_diff > 0, 0)
    losses = -price_diff.where(price_diff < 0, 0)
    avg_gain = gains.ewm(span=window_length, adjust=False).mean()
    avg_loss = losses.ewm(span=window_length, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else "N/A"

def calculate_stochastic_oscillator(close_prices, high_prices, low_prices, window_length=14):
    lowest_low = low_prices.rolling(window=window_length).min()
    highest_high = high_prices.rolling(window=window_length).max()

    stochastic_k = ((close_prices - lowest_low) / (highest_high - lowest_low)) * 100
    stochastic_d = stochastic_k.rolling(window=3).mean()

    return stochastic_k.iloc[-1], stochastic_d.iloc[-1]

def suggestion(last_price, ema_5, median_bollinger, ema, spread):
    if (last_price + (2 * spread)) < ema_5 < median_bollinger < ema:
        return "BUY"
    elif (last_price - (2 * spread)) > ema_5 > median_bollinger > ema:
        return "SELL"
    else:
        return "NEUTRAL"

def send_startup_message():
    startup_message = "SCALPING SIGNAL PROGRAM AVVIATO"
    send_telegram_message(startup_message)

    for stock_symbol in prev_status_dict.keys():
        stock_price(stock_symbol, 0.0, StringVar(), Label(), Label(), Label(), Label(), Label(), Label(), Label(), Label(), Label(), Label(), Label())
        stock_symbol_normalized = stock_symbol.replace(".", "_").replace("^", "_")
        update_buy_sell_label_and_send_message(stock_symbol_normalized, Label(), float("N/A"), float("N/A"), float("N/A"), float("N/A"), 0.0, float("N/A"), float("N/A"), float("N/A"), float("N/A"))

def update_buy_sell_label_and_send_message(stock_symbol, buy_sell_label, last_price, ema_5, median_bollinger, ema, spread, rsi_5, rsi, stochastic_k, stochastic_d):
    global last_message_time
    global prev_status_dict

    stock_symbol_normalized = stock_symbol.replace(".", "_").replace("^", "_")

    # Aggiorna in modo sincronizzato
    with lock:
        if stock_symbol_normalized not in prev_status_dict:
            prev_status_dict[stock_symbol_normalized] = "NEUTRAL"

        current_status = suggestion(last_price, ema_5, median_bollinger, ema, spread)
        buy_sell_label.config(text=current_status, fg="green" if current_status == "BUY" else "red" if current_status == "SELL" else "white")

        if current_status in ["BUY", "SELL"] and prev_status_dict[stock_symbol_normalized] != current_status:
            message = f"Status changed: {prev_status_dict[stock_symbol_normalized]} -> {current_status}\n\n"
            message += f"Asset: {stock_symbol}\n"
            message += f"Spread: {spread:.4f}\n"
            message += f"Price: {last_price:.4f}\n"
            message += f"EMA(5): {ema_5:.3f}\n"
            message += f"Median Bollinger: {median_bollinger:.3f}\n"
            message += f"EMA(40): {ema:.3f}\n"
            message += f"RSI(5) 70/30: {rsi_5:.3f}\n"
            message += f"RSI(20) 70/30: {rsi:.3f}\n"
            message += f"Stochastic (K/D) 80/20: {stochastic_k:.3f} / {stochastic_d:.3f}\n"
            message += f"Update Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

            send_telegram_message(message)
            last_message_time = time.time()

        if current_status == "NEUTRAL":
            # Resetta lo stato precedente quando torna a NEUTRAL
            prev_status_dict[stock_symbol_normalized] = "NEUTRAL"

    prev_status_dict[stock_symbol_normalized] = current_status

def stock_price(stock_symbol, spread, result_var, ema_label, ema_5_label, rsi_5_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label):
    stock = yf.Ticker(stock_symbol)
    info = stock.history(period='1d', interval='5m') 
    last_price = info['Close'].iloc[-1] if not info.empty else "N/A"
    result_var.set("{:,.3f}".format(last_price))

    ema_5 = info['Close'].ewm(span=5, adjust=False).mean().iloc[-1] if not info.empty else "N/A"
    ema_5_label.config(text=f"EMA(5 Close): {format(ema_5, ',.3f')}")    

    ema = info['Close'].ewm(span=40, adjust=False).mean().iloc[-1] if not info.empty else "N/A"
    ema_label.config(text=f"EMA(40 Close): {format(ema, ',.3f')}")

    rolling_mean = info['Close'].rolling(window=25).mean().iloc[-1] if not info.empty else "N/A"
    rolling_std = info['Close'].rolling(window=25).std().iloc[-1] if not info.empty else "N/A"
    upper_band = rolling_mean + 2 * rolling_std
    lower_band = rolling_mean - 2 * rolling_std

    median_bollinger = (lower_band + upper_band) / 2
    median_bollinger_label.config(text=f"Median Bollinger: {format(median_bollinger, ',.3f')}")

    bollinger_label.config(text=f"Bollinger Bands(25): {format(lower_band, ',.3f')} - {format(upper_band, ',.3f')}")

    rsi_5 = calculate_rsi(info['Close'], 5)
    rsi_5_label.config(text=f"RSI(5) - IPERCOMPRATO > 70 / IPERVENDUTO < 30: {format(rsi_5, ',.3f')}")

    rsi = calculate_rsi(info['Close'], 20)
    rsi_label.config(text=f"RSI(20) - IPERCOMPRATO > 70 / IPERVENDUTO < 30: {format(rsi, ',.3f')}")

    stochastic_k, stochastic_d = calculate_stochastic_oscillator(info['Close'], info['High'], info['Low'], 14)
    stoch_label.config(text=f"Stochastic Oscillator (K/D) - IPERCOMPRATO > 80 / IPERVENDUTO < 20: {format(stochastic_k, ',.3f')} / {format(stochastic_d, ',.3f')}")

    update_buy_sell_label_and_send_message(stock_symbol, buy_sell_label, last_price, ema_5, median_bollinger, ema, spread, rsi_5, rsi, stochastic_k, stochastic_d)

    update_label.config(text="Ultimo aggiornamento: {}".format(time.strftime("%H:%M:%S")))

def update_stock_data(stock_symbol, spread, result_var, ema_label, ema_5_label, rsi_5_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label):
    update_label.config(text="Updating...")

    stock = yf.Ticker(stock_symbol)
    info = stock.history(period='1d', interval='5m') 
    last_price = info['Close'].iloc[-1] if not info.empty else "N/A"
    result_var.set("{:,.3f}".format(last_price))

    ema_5 = info['Close'].ewm(span=5, adjust=False).mean().iloc[-1] if not info.empty else "N/A"
    ema_5_label.config(text=f"EMA(5 Close): {format(ema_5, ',.3f')}")    

    ema = info['Close'].ewm(span=40, adjust=False).mean().iloc[-1] if not info.empty else "N/A"
    ema_label.config(text=f"EMA(40 Close): {format(ema, ',.3f')}")

    rolling_mean = info['Close'].rolling(window=25).mean().iloc[-1] if not info.empty else "N/A"
    rolling_std = info['Close'].rolling(window=25).std().iloc[-1] if not info.empty else "N/A"
    upper_band = rolling_mean + 2 * rolling_std
    lower_band = rolling_mean - 2 * rolling_std

    median_bollinger = (lower_band + upper_band) / 2
    median_bollinger_label.config(text=f"Median Bollinger: {format(median_bollinger, ',.3f')}")

    bollinger_label.config(text=f"Bollinger Bands(25): {format(lower_band, ',.3f')} - {format(upper_band, ',.3f')}")

    rsi_5 = calculate_rsi(info['Close'], 5)
    rsi_5_label.config(text=f"RSI(5) - IPERCOMPRATO > 70 / IPERVENDUTO < 30: {format(rsi_5, ',.3f')}")

    rsi = calculate_rsi(info['Close'], 20)
    rsi_label.config(text=f"RSI(20) - IPERCOMPRATO > 70 / IPERVENDUTO < 30: {format(rsi, ',.3f')}")

    stochastic_k, stochastic_d = calculate_stochastic_oscillator(info['Close'], info['High'], info['Low'], 14)
    stoch_label.config(text=f"Stochastic Oscillator (K/D) - IPERCOMPRATO > 80 / IPERVENDUTO < 20: {format(stochastic_k, ',.3f')} / {format(stochastic_d, ',.3f')}")

    update_buy_sell_label_and_send_message(stock_symbol, buy_sell_label, last_price, ema_5, median_bollinger, ema, spread, rsi_5, rsi, stochastic_k, stochastic_d)

    update_label.config(text="Ultimo aggiornamento: {}".format(time.strftime("%H:%M:%S")))
    
    # Chiamare nuovamente la funzione dopo 10 secondi
    root.after(10000, lambda: update_stock_data(stock_symbol, spread, result_var, ema_label, ema_5_label, rsi_5_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label))

def update_all_stocks():
    for stock_symbol in prev_status_dict.keys():
        stock_symbol_normalized = stock_symbol.replace(".", "_").replace("^", "_")
        # Aggiornare i dati per la prima volta
        update_stock_data(stock_symbol, 0.0, StringVar(), Label(), Label(), Label(), Label(), Label(), Label(), Label(), Label(), Label())

    # Richiamare la funzione dopo 10 secondi
    root.after(10000, update_all_stocks)

def load_file():
    file_path = filedialog.askopenfilename(title="Select TXT File", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'r') as file:
            for line in file:
                asset, spread = line.strip().split(', ')
                stock_window = create_stock_window(asset, float(spread))
                # Call update_stock_data for each asset
                threading.Thread(target=update_stock_data, args=(asset, float(spread), StringVar(), stock_window.ema_label, stock_window.ema_5_label, stock_window.rsi_5_label, stock_window.bollinger_label, stock_window.median_bollinger_label, stock_window.rsi_label, stock_window.stoch_label, stock_window.buy_sell_label, stock_window.update_label)).start()

def create_stock_window(asset="", spread=""):
    def update_stock_data_wrapper():
        threading.Thread(target=update_stock_data, args=(stock_symbol_entry.get(), float(spread_entry.get()) if spread_entry.get() else 0.0, result_var, stock_window.ema_label, stock_window.ema_5_label, stock_window.rsi_5_label, stock_window.bollinger_label, stock_window.median_bollinger_label, stock_window.rsi_label, stock_window.stoch_label, stock_window.buy_sell_label, stock_window.update_label)).start()

    stock_window = Toplevel(root)
    stock_window.title("Stock Monitor")

    Label(stock_window, text="Asset: ").grid(row=0, column=0, sticky=W)
    Label(stock_window, text="Spread: ").grid(row=1, column=0, sticky=W)
    Label(stock_window, text="Stock Result:").grid(row=3, column=0, sticky=W)

    result_var = StringVar()
    result_label = Label(stock_window, textvariable=result_var)
    result_label.grid(row=3, column=1, sticky=W)

    stock_symbol_entry = Entry(stock_window)
    stock_symbol_entry.grid(row=0, column=1)
    stock_symbol_entry.insert(0, asset)

    spread_entry = Entry(stock_window)
    spread_entry.grid(row=1, column=1)
    spread_entry.insert(0, spread)

    show_button = Button(stock_window, text="Show", command=update_stock_data_wrapper)
    show_button.grid(row=0, column=2, columnspan=2, rowspan=2, padx=5, pady=5)

    stock_window.ema_5_label = Label(stock_window, text="")
    stock_window.ema_5_label.grid(row=4, column=0, columnspan=2, pady=5, sticky=W)

    stock_window.ema_label = Label(stock_window, text="")
    stock_window.ema_label.grid(row=7, column=0, columnspan=2, pady=5, sticky=W)

    stock_window.bollinger_label = Label(stock_window, text="")
    stock_window.bollinger_label.grid(row=8, column=0, columnspan=2, pady=5, sticky=W)

    stock_window.median_bollinger_label = Label(stock_window, text="")
    stock_window.median_bollinger_label.grid(row=5, column=0, columnspan=2, pady=5, sticky=W)

    stock_window.rsi_5_label = Label(stock_window, text="")
    stock_window.rsi_5_label.grid(row=9, column=0, columnspan=2, pady=5, sticky=W)

    stock_window.rsi_label = Label(stock_window, text="")
    stock_window.rsi_label.grid(row=10, column=0, columnspan=2, pady=5, sticky=W)

    stock_window.stoch_label = Label(stock_window, text="")
    stock_window.stoch_label.grid(row=11, column=0, columnspan=2, pady=5, sticky=W)

    stock_window.buy_sell_label = Label(stock_window, text="", fg="white", bg="black")
    stock_window.buy_sell_label.grid(row=12, column=0, columnspan=2, pady=5, sticky=W)

    stock_window.update_label = Label(stock_window, text="")
    stock_window.update_label.grid(row=13, column=0, columnspan=4, pady=5)

    update_stock_data_wrapper()  # Update stock data immediately when the window is created

    stock_price.jobs = []

    return stock_window

if __name__ == "__main__":
    root = Tk()

    add_button = Button(root, text="ADD", command=create_stock_window)
    add_button.pack(pady=10)

    load_button = Button(root, text="LOAD", command=load_file)
    load_button.pack(pady=10)

    prev_status = "NEUTRAL"

    send_startup_message()

    # Avvia un thread per aggiornare automaticamente tutti gli asset
    threading.Thread(target=update_all_stocks).start()

    root.mainloop()
