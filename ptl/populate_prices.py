import sqlite3, config
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit


connection = sqlite3.connect(config.DB_FILE)

connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id, symbol, name FROM stock
""")

rows = cursor.fetchall()

symbols = []
stock_dict = {}
for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

chunk_size = 200
for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]

    barsets = api.get_bars(symbol_chunk, TimeFrame(5, TimeFrameUnit.Minute),"2023-08-21", "2023-08-21", adjustment='raw').df
    print(barsets)
    # barsets = api.get_bars(['AAPL', 'MSFT'], TimeFrame(5, TimeFrameUnit.Minute), "2023-08-21", "2023-08-21",
    #                        adjustment='raw').df

    # for symbol in barsets:
    #     print(f"processing symbol {symbol}")
    #     for bar in barsets[symbol]:
    #         stock_id = stock_dict[symbol]
    #         cursor.execute("""
    #             INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
    #             VALUES (?, ?, ?, ?, ?, ?, ?)
    #         """, (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v))

connection.commit()
