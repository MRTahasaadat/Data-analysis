# 📊 Financial Data Analysis Dashboard  

## 📊 داشبورد تحلیل داده‌های مالی

An advanced Streamlit dashboard for real-time financial data visualization and news monitoring using Yahoo Finance and NewsAPI.  

داشبورد پیشرفته‌ای با Streamlit برای نمایش داده‌های زنده بازارهای مالی و مشاهده اخبار مرتبط با استفاده از Yahoo Finance و NewsAPI.

---

## 🚀 Features  

## 🚀 ویژگی‌ها

- 📈 Live financial data from stocks, crypto, and gold

  📈 دریافت داده‌های زنده برای سهام، رمزارزها و طلا
  
- 📅 Custom date range selection
  📅 امکان انتخاب بازه زمانی دلخواه
  
- 🕯 Candlestick chart for price analysis
 
  🕯 نمودار شمعی برای تحلیل دقیق قیمت
  

- 📉 Separate plots for:

   - Daily close prices

  - Percent Benefit

   - Tolerance  
  
  📉 نمودارهای جداگانه برای:

  - قیمت پایانی روزانه

  - درصد سود یا زیان

  - تلورانس قیمتی
    
- 📰 Real-time news based on selected asset
  
  📰 دریافت اخبار مرتبط با دارایی انتخاب‌شده
  
- 🖤 Dark mode design
  
  🖤 طراحی تاریک برای راحتی چشم
  
- 🎛 Manual refresh with button (no auto-refresh)
  
  🎛 به‌روزرسانی دستی با دکمه (بدون تازه‌سازی خودکار)
  

---

## 🧰 Technologies  

## 🧰 تکنولوژی‌ها

    - Python 3.x  
    - Streamlit  
    - Plotly  
    - yfinance  
    - NewsAPI  
    - Pandas  
    - Requests  
    - dotenv  

---


### 1. Clone the repository  

### ۱. دریافت پروژه:

```bash
https://github.com/MRTahasaadat/Data-analysis/edit/main/Financial%20data%20analysis.git


2. Install dependencies
۲. نصب وابستگی‌ها:

python -m venv venv
source venv/bin/activate
# Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Add .env file with your News API key
۳. افزودن فایل .env شامل کلید NewsAPI:

NEWS_API_KEY=your_api_key_here

4. Run the app
۴. اجرای برنامه:

streamlit run main.py

🖼 Sample Screenshots
🖼 تصاویر نمونه
Dashboard	Candlestick
	
⚠️ Notes
⚠️ نکات مهم

    Yahoo Finance limits 1-minute data to last 7 days only
    برای داده‌های دقیقه‌ای، یاهو فقط ۷ روز اخیر را پشتیبانی می‌کند.

    If longer range is selected, the interval auto-adjusts to daily
    اگر بازه بلندتر انتخاب شود، بازه به صورت خودکار به حالت روزانه تنظیم می‌شود.

    News opens in a new browser tab with smaller font
    اخبار در تب جدید مرورگر و با فونت کوچک‌تر نمایش داده می‌شود.

👤 Developer
👤 توسعه‌دهنده

    Name / نام: [https://github.com/MRTahasaadat.git]

    Email / ایمیل: [mrtahasaadat@gmail.com]

    
