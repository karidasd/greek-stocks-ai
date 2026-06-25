import os
import json
import feedparser
import urllib.parse
from datetime import datetime
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
import pandas as pd

MARKETS = {
    "gr": {
        "name": "Greek Stocks",
        "news_query": "Χρηματιστήριο Αθηνών OR Οικονομία Ελλάδα",
        "lang": "el",
        "stocks": [
            {"ticker": "OPAP.AT", "name": "ΟΠΑΠ"},
            {"ticker": "PPC.AT", "name": "ΔΕΗ"},
            {"ticker": "HTO.AT", "name": "ΟΤΕ"},
            {"ticker": "ETE.AT", "name": "Εθνική Τράπεζα"},
            {"ticker": "METLEN.AT", "name": "Metlen"},
            {"ticker": "EUROB.AT", "name": "Eurobank"},
            {"ticker": "ALPHA.AT", "name": "Alpha Bank"},
            {"ticker": "TPEIR.AT", "name": "Τράπεζα Πειραιώς"},
            {"ticker": "MOH.AT", "name": "Motor Oil"},
            {"ticker": "TENERGY.AT", "name": "ΤΕΡΝΑ Ενεργειακή"},
            {"ticker": "ELPE.AT", "name": "HelleniQ Energy"},
            {"ticker": "GEKTERNA.AT", "name": "ΓΕΚ ΤΕΡΝΑ"},
            {"ticker": "TITC.AT", "name": "ΤΙΤΑΝ"},
            {"ticker": "CENER.AT", "name": "Cenergy"},
            {"ticker": "VIO.AT", "name": "Viohalco"}
        ]
    },
    "us": {
        "name": "US Tech",
        "news_query": "US Technology Stocks Wall Street",
        "lang": "en",
        "stocks": [
            {"ticker": "AAPL", "name": "Apple"},
            {"ticker": "MSFT", "name": "Microsoft"},
            {"ticker": "NVDA", "name": "Nvidia"},
            {"ticker": "TSLA", "name": "Tesla"},
            {"ticker": "GOOG", "name": "Alphabet"},
            {"ticker": "AMZN", "name": "Amazon"},
            {"ticker": "META", "name": "Meta"},
            {"ticker": "AMD", "name": "AMD"},
            {"ticker": "NFLX", "name": "Netflix"},
            {"ticker": "INTC", "name": "Intel"},
            {"ticker": "PLTR", "name": "Palantir"},
            {"ticker": "SMCI", "name": "Super Micro"},
            {"ticker": "ARM", "name": "ARM"},
            {"ticker": "AVGO", "name": "Broadcom"},
            {"ticker": "QCOM", "name": "Qualcomm"}
        ]
    },
    "crypto": {
        "name": "Crypto",
        "news_query": "Cryptocurrency Bitcoin Ethereum",
        "lang": "en",
        "stocks": [
            {"ticker": "BTC-USD", "name": "Bitcoin"},
            {"ticker": "ETH-USD", "name": "Ethereum"},
            {"ticker": "SOL-USD", "name": "Solana"},
            {"ticker": "BNB-USD", "name": "Binance Coin"},
            {"ticker": "XRP-USD", "name": "XRP"},
            {"ticker": "ADA-USD", "name": "Cardano"},
            {"ticker": "AVAX-USD", "name": "Avalanche"},
            {"ticker": "DOGE-USD", "name": "Dogecoin"},
            {"ticker": "LINK-USD", "name": "Chainlink"},
            {"ticker": "DOT-USD", "name": "Polkadot"},
            {"ticker": "POL-USD", "name": "Polygon"},
            {"ticker": "LTC-USD", "name": "Litecoin"},
            {"ticker": "NEAR-USD", "name": "NEAR"},
            {"ticker": "FET-USD", "name": "Fetch.ai"}
        ]
    }
}

analyzer = SentimentIntensityAnalyzer()
translator = GoogleTranslator(source='el', target='en')

def analyze_sentiment(company_name, lang="el"):
    query = urllib.parse.quote(f"{company_name} stock OR {company_name} financial" if lang == "en" else f"{company_name} μετοχη OR {company_name} χρηματιστηριο")
    hl = "en&gl=US&ceid=US:en" if lang == "en" else "el&gl=GR&ceid=GR:el"
    url = f"https://news.google.com/rss/search?q={query}&hl={hl}"
    
    feed = feedparser.parse(url)
    if not feed.entries:
        return "Neutral", 0.0

    scores = []
    
    for entry in feed.entries[:3]:
        title = entry.title
        try:
            if lang == "el":
                eval_title = translator.translate(title)
            else:
                eval_title = title
            sentiment_dict = analyzer.polarity_scores(eval_title)
            scores.append(sentiment_dict['compound'])
        except Exception as e:
            print(f"Error analyzing {title}: {e}")
            continue
            
    if not scores: return "Neutral", 0.0
    
    avg_score = sum(scores) / len(scores)
    
    if avg_score >= 0.15:
        return "Bullish", avg_score
    elif avg_score <= -0.15:
        return "Bearish", avg_score
    else:
        return "Neutral", avg_score

def fetch_market_news(query, lang="el"):
    hl = "en&gl=US&ceid=US:en" if lang == "en" else "el&gl=GR&ceid=GR:el"
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl={hl}"
    feed = feedparser.parse(url)
    news = []
    for entry in feed.entries[:5]:
        news.append({"title": entry.title, "link": entry.link})
    return news

def fetch_stock_data(stock, lang="el"):
    print(f"Fetching data for {stock['ticker']}...")
    ticker = yf.Ticker(stock['ticker'])
    
    df = ticker.history(period="1y")
    if df.empty or len(df) < 20:
        print(f"No data for {stock['ticker']}")
        return None
        
    current_price = float(df['Close'].iloc[-1])
    prev_price = float(df['Close'].iloc[-2])
    change_pct = ((current_price - prev_price) / prev_price) * 100
    
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    sma50 = df['Close'].rolling(window=50, min_periods=1).mean()
    sma200 = df['Close'].rolling(window=200, min_periods=1).mean()
    
    current_sma50 = float(sma50.iloc[-1])
    current_sma200 = float(sma200.iloc[-1])
    prev_sma50 = float(sma50.iloc[-2]) if len(sma50) > 1 else current_sma50
    prev_sma200 = float(sma200.iloc[-2]) if len(sma200) > 1 else current_sma200
    
    pattern = "Neutral"
    if current_sma50 > current_sma200 and prev_sma50 <= prev_sma200:
        pattern = "Golden Cross"
    elif current_sma50 < current_sma200 and prev_sma50 >= prev_sma200:
        pattern = "Death Cross"
    elif current_sma50 > current_sma200:
        pattern = "Bullish Trend"
    elif current_sma50 < current_sma200:
        pattern = "Bearish Trend"
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_series = 100 - (100 / (1 + rs))
    rsi = float(rsi_series.iloc[-1])
    
    sma20 = float(sma20)
    
    if pd.isna(rsi): rsi = 50.0
    if pd.isna(sma20): sma20 = current_price
    
    if rsi < 30 and current_price > sma20:
        tech_tip = "STRONG BUY"
    elif rsi < 40:
        tech_tip = "BUY"
    elif rsi > 70 and current_price < sma20:
        tech_tip = "STRONG SELL"
    elif rsi > 65:
        tech_tip = "SELL"
    else:
        tech_tip = "HOLD"

    sparkline = [float(p) for p in df['Close'].tail(7).values]
    
    avg_volume = df['Volume'].rolling(window=20, min_periods=1).mean().iloc[-1]
    today_volume = df['Volume'].iloc[-1]
    volume_breakout = bool(today_volume > (avg_volume * 1.5)) if avg_volume > 0 else False

    sentiment_badge, sentiment_score = analyze_sentiment(stock['name'], lang)

    info = ticker.info
    try:
        pe_ratio = info.get('trailingPE') or info.get('forwardPE') or 0
        pe_ratio = round(pe_ratio, 2) if pe_ratio else "N/A"
    except:
        pe_ratio = "N/A"
        
    try:
        div_yield = info.get('dividendYield') or 0
        div_yield = round(div_yield * 100, 2) if div_yield else 0
    except:
        div_yield = 0
        
    try:
        ex_div = info.get('exDividendDate')
        if ex_div:
            div_date = datetime.fromtimestamp(ex_div)
            days_to_div = (div_date - datetime.now()).days
            if 0 <= days_to_div <= 30:
                upcoming_event = f"Dividend in {days_to_div} days" if lang == "en" else f"Αποκοπή Μερίσματος σε {days_to_div} μέρες"
            else:
                upcoming_event = None
        else:
            upcoming_event = None
    except:
        upcoming_event = None

    return {
        "ticker": stock['ticker'],
        "name": stock['name'],
        "price": round(current_price, 3) if current_price < 1000 else round(current_price, 1),
        "change_pct": round(change_pct, 2),
        "rsi": round(rsi, 1),
        "tech_tip": tech_tip,
        "sentiment": sentiment_badge,
        "sentiment_score": round(sentiment_score, 2),
        "sparkline": sparkline,
        "volume_breakout": volume_breakout,
        "pattern": pattern,
        "pe_ratio": pe_ratio,
        "dividend_yield": div_yield,
        "upcoming_event": upcoming_event
    }

def process_market(market_id, market_data, data_dir):
    print(f"\n=== Processing Market: {market_data['name']} ===")
    results = []
    for stock in market_data['stocks']:
        try:
            data = fetch_stock_data(stock, market_data['lang'])
            if data:
                results.append(data)
        except Exception as e:
            print(f"Failed to process {stock['ticker']}: {e}")
            
    sotd = None
    best_score = -999
    
    for r in results:
        score = (50 - r['rsi']) + (r['sentiment_score'] * 50) 
        if r['tech_tip'] in ["BUY", "STRONG BUY"] and r['sentiment'] == "Bullish":
            score += 20
            
        if r['pattern'] == "Golden Cross": score += 30
        elif r['pattern'] == "Bullish Trend": score += 10
        elif r['pattern'] == "Death Cross": score -= 30
        
        if r['pe_ratio'] != "N/A" and isinstance(r['pe_ratio'], (int, float)) and r['pe_ratio'] < 15 and r['pe_ratio'] > 0: score += 10
        if r['dividend_yield'] > 3.0: score += 10
        if score > best_score:
            best_score = score
            sotd = r

    history_file = os.path.join(data_dir, f'history_{market_id}.json')
    history_data = []
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
            
    wins = 0
    total_valid = 0
    for h in history_data:
        curr_price = next((r['price'] for r in results if r['ticker'] == h['ticker']), None)
        if curr_price:
            total_valid += 1
            if curr_price > h['price_at_pick']:
                wins += 1
                
    win_rate = round((wins / total_valid) * 100, 1) if total_valid > 0 else 0
    
    if sotd:
        today_str = datetime.now().strftime('%Y-%m-%d')
        if not history_data or history_data[-1]['date'] != today_str:
            history_data.append({
                "date": today_str,
                "ticker": sotd['ticker'],
                "price_at_pick": sotd['price']
            })
            if len(history_data) > 30:
                history_data = history_data[-30:]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=4)

    if results:
        avg_rsi = sum(r['rsi'] for r in results) / len(results)
        avg_sent = sum(r['sentiment_score'] for r in results) / len(results)
        sent_100 = ((avg_sent + 1) / 2) * 100
        fear_greed_score = round((avg_rsi * 0.5) + (sent_100 * 0.5))
        if fear_greed_score > 65: fg_status = "Extreme Greed"
        elif fear_greed_score > 55: fg_status = "Greed"
        elif fear_greed_score < 35: fg_status = "Extreme Fear"
        elif fear_greed_score < 45: fg_status = "Fear"
        else: fg_status = "Neutral"
        fear_greed = {"score": fear_greed_score, "status": fg_status}
    else:
        fear_greed = {"score": 50, "status": "Neutral"}

    market_news = fetch_market_news(market_data['news_query'], market_data['lang'])

    output_file = os.path.join(data_dir, f'{market_id}.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json_data = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M'), 
            "market_name": market_data['name'],
            "stocks": results, 
            "sotd": sotd['ticker'] if sotd else None, 
            "fear_greed": fear_greed,
            "market_news": market_news,
            "sotd_win_rate": {"rate": win_rate, "total": total_valid}
        }
        json.dump(json_data, f, indent=4, ensure_ascii=False)
        
    print(f"Saved {len(results)} items for {market_id}.")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    for market_id, market_data in MARKETS.items():
        process_market(market_id, market_data, data_dir)

if __name__ == "__main__":
    main()
