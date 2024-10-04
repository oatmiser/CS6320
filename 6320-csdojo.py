import os
import telebot
import yfinance as yf


# https://www.youtube.com/watch?v=NwBWW8cNCP4
API_KEY = ""#os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=["greet"])
def greet(message):
    bot.reply_to(message, "How are you?")

@bot.message_handler(commands=["hello"])
def hello(message):
    bot.send_message(message.chat.id, "Hello!")

@bot.message_handler(commands=["wsb"])
def get_stocks(message):
    response = ""
    stocks = ["gme", "amc", "nok"]
    stock_data = []
    for stock in stocks:
        data = yf.download(tickers=stock, period="2d", interval="1d")
        data = data.reset_index()
        response += f"---{stock}---\n"
        stock_data.append([stock])
        columns = ["stock"]
        for index, row in data.iterrows():
            stock_position = len(stock_data) - 1
            price = round(row["Close"], 2)
            format_date = row["Date"].strftime("%m/%d")
            response += f"{format_date}: {price}\n"
            stock_data[stock_position].append(price)
            columns.append(format_date)
        print()

    response = f"{columns[0] :<10}{columns[1] :^10}{columns[2] :>10}\n"
    for row in stock_data:
        response += f"{row[0] :<10}{row[1] :^10}{row[2] :>10}\n"
    response += "\nStock Data"
    print(response)
    bot.send_message(message.chat.id, response)

def stock_request(message):
    # e.g. "price gme"
    # Test to see if message is possible to be a stock request
    request = message.text.split()
    if len(request)<2 or request[0].lower() not in "price":
        return False
    return True

@bot.message_handler(func=stock_request)
def send_price(message):
    request = message.text.split()[1]
    data = yf.download(tickers=request, period="6mo", interval="1mo")
    if data.size > 0:
        data = data.reset_index()
        data["format_date"] = data["Date"].dt.strftime("%m/%d %I:%M %p")
        data.set_index("format_date", inplace=True)
        print(data.to_string())
        bot.send_message(message.chat.id, data["Close"].to_string(header=False))
    else:
        bot.send_message(message.chat.id, "No data")

bot.polling()