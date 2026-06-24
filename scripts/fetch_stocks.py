import os
import json
import feedparser
import urllib.parse
from datetime import datetime
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
import pandas as pd

STOCKS = [
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

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(company_name):
    query = urllib.parse.quote(f"{company_name} μετοχη OR {company_name} χρηματιστηριο")
    url = f"https://news.google.com/rss/search?q={query}&hl=el&gl=GR&ceid=GR:el"
    
    feed = feedparser.parse(url)
    if not feed.entries:
        return "Neutral", 0.0

    scores = []
    translator = GoogleTranslator(source='el', target='en')
    
    # Analyze top 3 headlines
    for entry in feed.entries[:3]:
        title = entry.title
        try:
            english_title = translator.translate(title)
            sentiment_dict = analyzer.polarity_scores(english_title)
            scores.append(sentiment_dict['compound'])
        except Exception as e:
            print(f"Error translating {title}: {e}")
            continue
            
    if not scores: return "Neutral", 0.0
    
    avg_score = sum(scores) / len(scores)
    
    if avg_score >= 0.15:
        return "Bullish", avg_score
    elif avg_score <= -0.15:
        return "Bearish", avg_score
    else:
        return "Neutral", avg_score

def fetch_stock_data(stock):
    print(f"Fetching data for {stock['ticker']}...")
    ticker = yf.Ticker(stock['ticker'])
    
    # Get last 1 year to calculate long-term technicals (SMA-200)
    df = ticker.history(period="1y")
    if df.empty or len(df) < 20:
        print(f"No data for {stock['ticker']}")
        return None
        
    current_price = float(df['Close'].iloc[-1])
    prev_price = float(df['Close'].iloc[-2])
    change_pct = ((current_price - prev_price) / prev_price) * 100
    
    # Technical Indicators manually using pandas
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    # Calculate SMA-50 and SMA-200 for Pattern Recognition
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
    
    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_series = 100 - (100 / (1 + rs))
    rsi = float(rsi_series.iloc[-1])
    
    sma20 = float(sma20)
    
    if pd.isna(rsi): rsi = 50.0
    if pd.isna(sma20): sma20 = current_price
    
    # Determine Technical Tip
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

    # Get last 7 days for sparkline
    sparkline = [float(p) for p in df['Close'].tail(7).values]
    
    # Calculate Volume Breakout
    avg_volume = df['Volume'].rolling(window=20, min_periods=1).mean().iloc[-1]
    today_volume = df['Volume'].iloc[-1]
    volume_breakout = bool(today_volume > (avg_volume * 1.5)) if avg_volume > 0 else False

    # Fetch Sentiment
    sentiment_badge, sentiment_score = analyze_sentiment(stock['name'])

    # Fetch Fundamentals
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

    return {
        "ticker": stock['ticker'],
        "name": stock['name'],
        "price": round(current_price, 3),
        "change_pct": round(change_pct, 2),
        "rsi": round(rsi, 1),
        "tech_tip": tech_tip,
        "sentiment": sentiment_badge,
        "sentiment_score": round(sentiment_score, 2),
        "sparkline": sparkline,
        "volume_breakout": volume_breakout,
        "pattern": pattern,
        "pe_ratio": pe_ratio,
        "dividend_yield": div_yield
    }

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    results = []
    for stock in STOCKS:
        try:
            data = fetch_stock_data(stock)
            if data:
                results.append(data)
        except Exception as e:
            print(f"Failed to process {stock['ticker']}: {e}")
            
    # Determine Stock of the Day (best combo of RSI oversold and Bullish sentiment)
    sotd = None
    best_score = -999
    
    for r in results:
        score = (50 - r['rsi']) + (r['sentiment_score'] * 50) 
        if r['tech_tip'] in ["BUY", "STRONG BUY"] and r['sentiment'] == "Bullish":
            score += 20
            
        # V3 additions
        if r['pattern'] == "Golden Cross": score += 30
        elif r['pattern'] == "Bullish Trend": score += 10
        elif r['pattern'] == "Death Cross": score -= 30
        
        if r['pe_ratio'] != "N/A" and r['pe_ratio'] < 15 and r['pe_ratio'] > 0: score += 10
        if r['dividend_yield'] > 3.0: score += 10
        if score > best_score:
            best_score = score
            sotd = r

    # Calculate Fear & Greed Index
    if results:
        avg_rsi = sum(r['rsi'] for r in results) / len(results)
        avg_sent = sum(r['sentiment_score'] for r in results) / len(results)
        # Convert to 0-100 scale. RSI is already 0-100. Sentiment is -1 to 1.
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

    output_file = os.path.join(data_dir, 'stocks.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"date": datetime.now().strftime('%Y-%m-%d %H:%M'), "stocks": results, "sotd": sotd['ticker'] if sotd else None, "fear_greed": fear_greed}, f, indent=4, ensure_ascii=False)
        
    print(f"Saved {len(results)} stocks.")

if __name__ == "__main__":
    main()
