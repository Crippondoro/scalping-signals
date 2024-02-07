import yfinance as yf
from tkinter import *
import threading
import time

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
def stock_price(stock_symbol, spread, result_var, ema_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label):
    stock = yf.Ticker(stock_symbol)
    info = stock.history(period='1d', interval='5m') 
    last_price = info['Close'].iloc[-1] if not info.empty else "N/A"
    result_var.set("{:.3f}".format(last_price))

    ema = info['Close'].ewm(span=60, adjust=False).mean().iloc[-1] if not info.empty else "N/A"
    ema_label.config(text=f"EMA(50 Close): {format(ema, '.3f')}")

    rolling_mean = info['Close'].rolling(window=20).mean().iloc[-1] if not info.empty else "N/A"
    rolling_std = info['Close'].rolling(window=20).std().iloc[-1] if not info.empty else "N/A"
    upper_band = rolling_mean + 2 * rolling_std
    lower_band = rolling_mean - 2 * rolling_std
    bollinger_label.config(text=f"Bollinger Bands: {format(lower_band, '.3f')} - {format(upper_band, '.3f')}")

    median_bollinger = (lower_band + upper_band) / 2
    median_bollinger_label.config(text=f"Median Bollinger: {format(median_bollinger, '.3f')}")

    rsi = calculate_rsi(info['Close'], 14)
    rsi_label.config(text=f"RSI(14) - IPERCOMPRATO > 70 / IPERVENDUTO < 30: {format(rsi, '.3f')}")

    stochastic_k, stochastic_d = calculate_stochastic_oscillator(info['Close'], info['High'], info['Low'], 14)
    stoch_label.config(text=f"Stochastic Oscillator (K/D) - IPERCOMPRATO > 80 / IPERVENDUTO < 20: {format(stochastic_k, '.3f')} / {format(stochastic_d, '.3f')}")

    suggestion(buy_sell_label, last_price, median_bollinger, ema, spread)
    
    update_label.config(text="Ultimo aggiornamento: {}".format(time.strftime("%H:%M:%S")))

def update_stock_data(stock_symbol, spread, result_var, ema_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label):
    update_label.config(text="Aggiornamento in corso...")
    stock_price(stock_symbol, spread, result_var, ema_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label)
    update_label.config(text="Ultimo aggiornamento: {}".format(time.strftime("%H:%M:%S")))
    stock_price_job = root.after(10000, update_stock_data, stock_symbol, spread, result_var, ema_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label)
    stock_price.jobs.append(stock_price_job)

def suggestion(buy_sell_label, last_price, median_bollinger, ema, spread):
    if (last_price + (2 * spread)) < median_bollinger < ema:
        buy_sell_label.config(text="ACQUISTA", fg="green")
    elif (last_price - (2 * spread)) > median_bollinger > ema:
        buy_sell_label.config(text="VENDI", fg="red")
    else:
        buy_sell_label.config(text="NEUTRO", fg="white")

def create_stock_window():
    stock_window = Toplevel(root)
    stock_window.title("Stock Monitor")
    
    Label(stock_window, text="Company Symbol : ").grid(row=0, column=0, sticky=W)
    Label(stock_window, text="Spread: ").grid(row=1, column=0, sticky=W)
    Label(stock_window, text="Stock Result:").grid(row=3, column=0, sticky=W)

    result_var = StringVar()
    result_label = Label(stock_window, text="", textvariable=result_var)
    result_label.grid(row=3, column=1, sticky=W)

    stock_symbol_entry = Entry(stock_window)
    stock_symbol_entry.grid(row=0, column=1)

    spread_entry = Entry(stock_window)
    spread_entry.grid(row=1, column=1)

    show_button = Button(stock_window, text="Show", command=lambda: threading.Thread(target=update_stock_data, args=(stock_symbol_entry.get(), float(spread_entry.get()) if spread_entry.get() else 0.0, result_var, ema_label, bollinger_label, median_bollinger_label, rsi_label, stoch_label, buy_sell_label, update_label)).start())
    show_button.grid(row=0, column=2, columnspan=2, rowspan=2, padx=5, pady=5)

    ema_label = Label(stock_window, text="")
    ema_label.grid(row=4, column=0, columnspan=2, pady=5, sticky=W)

    bollinger_label = Label(stock_window, text="")
    bollinger_label.grid(row=5, column=0, columnspan=2, pady=5, sticky=W)

    median_bollinger_label = Label(stock_window, text="")
    median_bollinger_label.grid(row=6, column=0, columnspan=2, pady=5, sticky=W)

    rsi_label = Label(stock_window, text="")
    rsi_label.grid(row=7, column=0, columnspan=2, pady=5, sticky=W)

    stoch_label = Label(stock_window, text="")
    stoch_label.grid(row=8, column=0, columnspan=2, pady=5, sticky=W)

    buy_sell_label = Label(stock_window, text="", fg="white", bg="black")
    buy_sell_label.grid(row=9, column=0, columnspan=2, pady=5, sticky=W)

    update_label = Label(stock_window, text="")
    update_label.grid(row=10, column=0, columnspan=4, pady=5)

    stock_price.jobs = []

root = Tk()

add_button = Button(root, text="AGGIUNGI", command=create_stock_window)
add_button.pack(pady=10)

root.mainloop()
