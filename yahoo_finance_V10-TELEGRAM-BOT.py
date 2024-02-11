import yfinance as yf
from tkinter import *
from tkinter import filedialog
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import threading
import time

# Aggiungi il tuo token e chat_id Telegram
TELEGRAM_BOT_TOKEN = "YUOR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = YOUR_CHAT_ID

# Funzione per inviare messaggi Telegram
def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

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

def stock_price(stock_symbol, spread, result_var, ema_label, ema_5_label, rsi_5_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label, update_time):
    stock = yf.Ticker(stock_symbol)
    info = stock.history(period='3d', interval='5m') 
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

    suggestion(stock_symbol, buy_sell_label, last_price, ema_5, median_bollinger, ema, spread, rsi_5, rsi, stochastic_k, stochastic_d, update_time)
    
    update_label.config(text="Ultimo aggiornamento: {}".format(time.strftime("%H:%M:%S")))

def update_stock_data(stock_symbol, spread, result_var, ema_label, ema_5_label, rsi_5_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label):
    update_label.config(text="Updating...")
    update_time = time.strftime("%Y-%m-%d %H:%M:%S")
    stock_price(stock_symbol, spread, result_var, ema_label, ema_5_label, rsi_5_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label, update_time)
    update_label.config(text="Last update: {}".format(time.strftime("%H:%M:%S")))
    root.after(10000, update_stock_data, stock_symbol, spread, result_var, ema_label, ema_5_label, rsi_5_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label)

def suggestion(stock_symbol, buy_sell_label, last_price, ema_5, median_bollinger, ema, spread, rsi_5, rsi, stochastic_k, stochastic_d, update_time):
    current_state = buy_sell_label.cget("text")

    if (last_price + (2 * spread)) < ema_5 < median_bollinger < ema:
        new_state = "BUY"
    elif (last_price - (2 * spread)) > ema_5 > median_bollinger > ema:
        new_state = "SELL"
    else:
        new_state = "NEUTRAL"

    # Invia messaggio solo se c'è un cambio di stato da NEUTRAL a BUY o SELL
    if current_state != new_state and new_state in ["BUY", "SELL"]:
        message = f"Asset: {stock_symbol}\nState: {new_state}\nSpread: {spread:.4f}\nLast Price: {last_price:.4f}\nEMA(5): {ema_5:.4f}\nMedian Bollinger: {median_bollinger:.4f}\nEMA(40): {ema:.4f}\nRSI(5)-70/30: {rsi_5:.4f}\nRSI(20)-70/30: {rsi:.4f}\nStochastic (K/D)-80/20: {stochastic_k:.4f} / {stochastic_d:.4f}\nDataOra: {update_time}"

        send_telegram_message(message)

    buy_sell_label.config(text=new_state, fg="green" if new_state == "BUY" else "red" if new_state == "SELL" else "white")

# Aggiunta la definizione della funzione load_file
def load_file():
    file_path = filedialog.askopenfilename(title="Select TXT File", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'r') as file:
            for line in file:
                asset, spread = line.strip().split(', ')
                create_stock_window(asset, float(spread), auto_start=True)

def create_stock_window(stock_symbol, spread, auto_start=True):
    stock_window = Toplevel(root)
    stock_window.title("Stock Monitor")
    
    Label(stock_window, text="Asset: ").grid(row=0, column=0, sticky=W)
    Label(stock_window, text="Spread: ").grid(row=1, column=0, sticky=W)
    Label(stock_window, text="Stock Result:").grid(row=3, column=0, sticky=W)

    result_var = StringVar()
    result_label = Label(stock_window, text="", textvariable=result_var)
    result_label.grid(row=3, column=1, sticky=W)

    stock_symbol_entry = Entry(stock_window)
    stock_symbol_entry.insert(0, stock_symbol)
    stock_symbol_entry.grid(row=0, column=1)

    spread_entry = Entry(stock_window)
    spread_entry.insert(0, str(spread))
    spread_entry.grid(row=1, column=1)

    show_button = Button(stock_window, text="Show", command=lambda: threading.Thread(target=update_stock_data, args=(stock_symbol_entry.get(), float(spread_entry.get()) if spread_entry.get() else 0.0, result_var, ema_label, ema_5_label, rsi_5_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label)).start())
    show_button.grid(row=0, column=2, columnspan=2, rowspan=2, padx=5, pady=5)

    ema_5_label = Label(stock_window, text="")
    ema_5_label.grid(row=4, column=0, columnspan=2, pady=5, sticky=W)

    ema_label = Label(stock_window, text="")
    ema_label.grid(row=7, column=0, columnspan=2, pady=5, sticky=W)

    bollinger_label = Label(stock_window, text="")
    bollinger_label.grid(row=8, column=0, columnspan=2, pady=5, sticky=W)

    median_bollinger_label = Label(stock_window, text="")
    median_bollinger_label.grid(row=5, column=0, columnspan=2, pady=5, sticky=W)

    rsi_5_label = Label(stock_window, text="")
    rsi_5_label.grid(row=9, column=0, columnspan=2, pady=5, sticky=W)

    rsi_label = Label(stock_window, text="")
    rsi_label.grid(row=10, column=0, columnspan=2, pady=5, sticky=W)

    stoch_label = Label(stock_window, text="")
    stoch_label.grid(row=11, column=0, columnspan=2, pady=5, sticky=W)

    buy_sell_label = Label(stock_window, text="", fg="white", bg="black")
    buy_sell_label.grid(row=12, column=0, columnspan=2, pady=5, sticky=W)

    update_label = Label(stock_window, text="")
    update_label.grid(row=13, column=0, columnspan=4, pady=5)

    if auto_start:
        update_stock_data(stock_symbol, spread, result_var, ema_label, ema_5_label, rsi_5_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label)

if __name__ == "__main__":
    # Invia messaggio di avvio del programma
    send_telegram_message("SCALPING SIGNAL PROGRAM AVVIATO")
    
    root = Tk()

    add_button = Button(root, text="ADD", command=lambda: create_stock_window("", 0.0))
    add_button.pack(pady=10)

    load_button = Button(root, text="LOAD", command=load_file)
    load_button.pack(pady=10)

    root.mainloop()


