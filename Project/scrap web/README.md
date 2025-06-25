#  Web Scraper for Mehr News - Economy Section 

اسکریپر وب برای بخش اقتصاد خبرگزاری مهر

This is a simple Python script to extract all paragraph texts (`<p>` tags) from the [Mehr News Economy section](https://www.mehrnews.com/service/Economy) and save them in a CSV file.

این اسکریپت پایتون، تمام پاراگراف‌ها (تگ‌های `<p>`) موجود در [بخش اقتصاد خبرگزاری مهر](https://www.mehrnews.com/service/Economy) را استخراج کرده و در یک فایل CSV ذخیره می‌کند.

---

##  Features | ویژگی‌ها

- Extracts all `<p>` tag content from the target page  
- Saves the data in a CSV file (`paragraphs.csv`)  
- Simple and fast web scraping using `requests` and `BeautifulSoup`

- استخراج تمام محتوای تگ‌های `<p>` از صفحه‌ی مورد نظر  
- ذخیره اطلاعات در قالب فایل CSV به نام `paragraphs.csv`  
- استفاده‌ی ساده و سریع از کتابخانه‌های `requests` و `BeautifulSoup`

---

##  Requirements | پیش‌نیازها

- Python 3.x  
- `requests`  
- `beautifulsoup4`  
- `pandas`

### Installation | نصب کتابخانه‌ها:

```bash
pip install requests beautifulsoup4 pandas

 How to Use | نحوه استفاده

    Save the code into a file, e.g., mehr_parser.py

    Run the script:

    python mehr_parser.py

    A file named paragraphs.csv will be generated in the same directory.

۱. کد را در فایلی مانند mehr_parser.py ذخیره کنید
۲. اسکریپت را اجرا کنید:

python mehr_parser.py

۳. فایل paragraphs.csv در همان مسیر ایجاد می‌شود.
 Output Format | قالب خروجی

CSV file with one column:
Paragraph Text
Example content from paragraph...
Another line from the website...

فایلی با فرمت CSV شامل یک ستون:
متن پاراگراف
محتوای پاراگراف نمونه...
یک خط دیگر از وب‌سایت...
 Notes | نکات مهم

    This script only scrapes the main Economy section page, not individual news articles.

    The HTML structure may change, which could break the script.

    Please follow ethical scraping practices and check the website’s robots.txt file.

    این اسکریپت فقط صفحه‌ی اصلی بخش اقتصاد را بررسی می‌کند، نه صفحات جزئیات خبر.

    ممکن است ساختار HTML سایت تغییر کند و باعث اختلال در عملکرد کد شود.

    لطفاً با رعایت اصول اخلاقی و قوانین سایت از اسکریپر استفاده کنید.

 Future Improvements | پیشنهادهای توسعه

    Support for pagination (multiple pages)

    Extracting article titles and URLs

    Saving in JSON or a database

    Add a simple GUI or web interface

    پشتیبانی از صفحات بعدی (pagination)

    استخراج عنوان خبر و لینک

    ذخیره داده در فرمت JSON یا پایگاه داده

    افزودن رابط کاربری گرافیکی یا تحت وب

 Author | نویسنده

Developed by [(https://github.com/MRTahasaadat)]
Email: [mrtahasaadat@gmail.com]
