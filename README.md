# 📈 ATHEX.AI | Greek Stocks AI Dashboard

![ATHEX.AI Banner](https://img.shields.io/badge/ATHEX.AI-Institutional%20Grade%20Analytics-3b82f6?style=for-the-badge)
![Automated](https://img.shields.io/badge/Automated-GitHub%20Actions-10b981?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

Ένα πλήρως αυτοματοποιημένο, "Institutional Grade" AI Dashboard για το **Ελληνικό Χρηματιστήριο (ΧΑΑ)**. Συνδυάζει **Τεχνική Ανάλυση** μέσω μαθηματικών μοντέλων και **Ανάλυση Συναισθήματος (Sentiment NLP)** μέσω ειδήσεων, προσφέροντας επαγγελματικά εργαλεία σε ένα δωρεάν περιβάλλον.

🔗 **[Live Demo (GitHub Pages)](https://karidasd.github.io/greek-stocks-ai/)**

---

## ✨ Βασικά Χαρακτηριστικά (Features)

- **🤖 Sentiment Analysis (NLP)**: Σαρώνει καθημερινά το Google News για ελληνικές ειδήσεις γύρω από τις μετοχές, τις μεταφράζει ακαριαία, και τρέχει τον αλγόριθμο `VADER` για να κρίνει αν το κλίμα είναι *Bullish* ή *Bearish*.
- **📊 Τεχνική Ανάλυση (RSI & MAs)**: Υπολογίζει δυναμικά το Relative Strength Index (RSI 14 ημερών) και εξάγει σήματα *STRONG BUY*, *BUY*, *HOLD*, ή *SELL*.
- **🌟 Αναγνώριση Μοτίβων**: Εντοπίζει κρίσιμα τεχνικά μοτίβα συγκρίνοντας τους Κινητούς Μέσους Όρους 50 και 200 ημερών (π.χ. **Golden Cross** / **Death Cross**).
- **🔥 Volume Breakouts**: Εντοπίζει και επισημαίνει μετοχές που παρουσιάζουν ασυνήθιστα υψηλό όγκο συναλλαγών (>150% του μέσου όρου 20 ημερών).
- **🏦 Θεμελιώδη (Fundamentals)**: Τραβάει αυτόματα το **P/E Ratio** και τη **Μερισματική Απόδοση (Dividend Yield)**.
- **🧭 ATHEX Fear & Greed Index**: Ένας πρωτοποριακός δείκτης-κοντέρ που συνδυάζει τους μέσους όρους του RSI και του News Sentiment όλης της αγοράς, για να υπολογίσει το συνολικό κλίμα (Φόβος ή Απληστία).
- **⚙️ Πλήρης Αυτοματισμός**: Ενημερώνεται 100% αυτόματα κάθε απόγευμα (Δευτέρα-Παρασκευή) μέσω **GitHub Actions**.

---

## 🛠️ Τεχνολογίες & Υποδομή

- **Backend (Python)**: `yfinance` (Δεδομένα αγοράς), `pandas` (Υπολογισμοί δεικτών), `vaderSentiment` & `deep-translator` (NLP & Μετάφραση), `feedparser` (Ειδήσεις).
- **Frontend (HTML/CSS/JS)**: Responsive "Glassmorphism" UI με Dark/Neon VIP αισθητική. Δυναμικά SVG Mini-Charts (Sparklines) και ζωντανά φίλτρα ταξινόμησης (Vanilla JS).
- **Hosting**: GitHub Pages (Εντελώς δωρεάν, Serverless Hosting).

---

## 🚀 Πώς να το τρέξετε Τοπικά

1. Κάντε Clone το repository:
   ```bash
   git clone https://github.com/karidasd/greek-stocks-ai.git
   cd greek-stocks-ai
   ```

2. Εγκαταστήστε τις βιβλιοθήκες της Python:
   ```bash
   pip install -r requirements.txt
   ```

3. Τρέξτε το Data Script για να ενημερώσετε το αρχείο `data/stocks.json`:
   ```bash
   python scripts/fetch_stocks.py
   ```

4. Ανοίξτε το αρχείο `index.html` στον Browser της επιλογής σας!

---

## ⚠️ Αποποίηση Ευθυνών (Disclaimer)

Το παρόν project αποτελεί καθαρά **πειραματικό εργαλείο** αλγοριθμικής ανάλυσης δεδομένων και ανάλυσης συναισθήματος (Sentiment NLP). 

Σε καμία περίπτωση **ΔΕΝ αποτελεί επενδυτική συμβουλή**, προτροπή, ή πρόταση αγοράς/πώλησης μετοχών ή άλλων χρηματοοικονομικών προϊόντων. Ο κώδικας, τα δεδομένα από τρίτες πηγές (Yahoo Finance, Google News) και τα AI μοντέλα ενδέχεται να περιέχουν σφάλματα, καθυστερήσεις ή ανακρίβειες. Ο δημιουργός δε φέρει καμία απολύτως ευθύνη για οποιαδήποτε οικονομική ζημία προκύψει από τη χρήση της εφαρμογής. Ο σκοπός της σελίδας είναι αυστηρά εκπαιδευτικός, ερευνητικός και προγραμματιστικός.
