

This Python script visualizes the top 10 most populated cities in Iran on a map, with interactive population charts on click. / این اسکریپت پایتون 10 شهر پرجمعیت ایران را بر روی نقشه به تصویر می‌کشد، با نمودارهای تعاملی جمعیت با کلیک.

## Overview / نمای کلی

The script uses `pandas` for data handling, `geopandas` for map plotting, `matplotlib` for visualization, and `mplcursors` for interactive data display. It plots the cities on a map of Iran and displays a bar chart of the city's population when a city marker is clicked. / این اسکریپت از `pandas` برای مدیریت داده، `geopandas` برای رسم نقشه، `matplotlib` برای تجسم و `mplcursors` برای نمایش تعاملی داده‌ها استفاده می‌کند. شهرها را روی نقشه ایران رسم می‌کند و نمودار میله‌ای جمعیت شهر را هنگام کلیک بر روی نشانگر شهر نمایش می‌دهد.

## Features / امکانات

*   **Map Visualization:** Displays a map of Iran using GeoJSON data. / **تجسم نقشه:** نمایش نقشه ایران با استفاده از داده‌های GeoJSON.
*   **City Markers:** Overlays the map with markers representing the top 10 most populated cities in Iran. / **نشانگرهای شهر:** پوشاندن نقشه با نشانگرهایی که 10 شهر پرجمعیت ایران را نشان می‌دهند.
*   **Interactive Population Charts:** When a city marker is clicked, a bar chart showing the population of that city is displayed. / **نمودارهای تعاملی جمعیت:** وقتی روی یک نشانگر شهر کلیک شود، نمودار میله‌ای که جمعیت آن شهر را نشان می‌دهد نمایش داده می‌شود.
*   **Clear Labels:** Provides labels for the map, axes, and charts, making it easy to understand. / **برچسب‌های واضح:** برچسب‌هایی برای نقشه، محورها و نمودارها ارائه می‌دهد که درک آن را آسان می‌کند.

## Requirements / الزامات

*   Python 3.x
*   Libraries: / کتابخانه‌ها:
    *   pandas
    *   geopandas
    *   matplotlib
    *   mplcursors

Install the required libraries using pip: / نصب کتابخانه‌های مورد نیاز با استفاده از pip:

```bash
pip install pandas geopandas matplotlib mplcursors

You will also need a GeoJSON file containing the map of Iran (e.g., iran_geo.json). Make sure this file is in the same directory as the script, or update the file path accordingly. / شما همچنین به یک فایل GeoJSON حاوی نقشه ایران نیاز دارید (مثلاً iran_geo.json). مطمئن شوید که این فایل در همان دایرکتوری اسکریپت قرار دارد، یا مسیر فایل را بر این اساس به‌روز کنید.
Usage / نحوه استفاده

    Save the script to a file (e.g., iran_cities.py). / اسکریپت را در یک فایل ذخیره کنید (مثلاً iran_cities.py).
    Ensure you have the iran_geo.json file in the same directory. / اطمینان حاصل کنید که فایل iran_geo.json در همان دایرکتوری قرار دارد.
    Run the script: / اسکریپت را اجرا کنید:

        

bash
python iran_cities.py

A map will be displayed with city markers. Click on a marker to see the population chart for that city. / نقشه با نشانگرهای شهر نمایش داده می‌شود. برای دیدن نمودار جمعیت آن شهر روی یک نشانگر کلیک کنید.
Code Explanation / توضیح کد

    Import Libraries: / وارد کردن کتابخانه‌ها:
        Imports necessary libraries (pandas, geopandas, matplotlib.pyplot, mplcursors). / کتابخانه‌های لازم را وارد می‌کند (pandas, geopandas, matplotlib.pyplot, mplcursors).
    City Data: / داده‌های شهر:
        Creates a pandas DataFrame containing data for the top 10 cities (City, Latitude, Longitude, Population). / یک pandas DataFrame ایجاد می‌کند که حاوی داده‌های 10 شهر برتر (شهر، عرض جغرافیایی، طول جغرافیایی، جمعیت) است.
    Map Loading: / بارگیری نقشه:
        Loads the map of Iran from the iran_geo.json file using geopandas. / نقشه ایران را از فایل iran_geo.json با استفاده از geopandas بارگیری می‌کند.
    Map Plotting: / رسم نقشه:
        Creates a plot using matplotlib and plots the map of Iran. / یک طرح با استفاده از matplotlib ایجاد می‌کند و نقشه ایران را رسم می‌کند.
        Adds scatter points for each city, using latitude and longitude. / نقاط پراکنده را برای هر شهر با استفاده از عرض و طول جغرافیایی اضافه می‌کند.
        Adds labels to each city point for easy identification. / برچسب‌هایی را برای هر نقطه شهر برای شناسایی آسان اضافه می‌کند.
    Interactive Function: / تابع تعاملی:
        Defines a function show_population(index) that displays a population bar chart for a given city index. / تابعی به نام show_population(index) را تعریف می‌کند که نمودار میله‌ای جمعیت را برای یک شاخص شهر معین نمایش می‌دهد.
        Uses mplcursors to connect the scatter plot to the show_population function, so that clicking on a point triggers the chart display. / از mplcursors برای اتصال طرح پراکنده به تابع show_population استفاده می‌کند، به طوری که کلیک کردن روی یک نقطه باعث نمایش نمودار می‌شود.
    Display Map: / نمایش نقشه:
        Shows the map with city markers and enables interactive population charts. / نقشه را با نشانگرهای شهر نشان می‌دهد و نمودارهای تعاملی جمعیت را فعال می‌کند.

Data Source / منبع داده

    City Data: The city data (names, coordinates, and population) was manually entered. Consider finding a reliable, up-to-date source for this data. / داده‌های شهر: داده‌های شهر (نام‌ها، مختصات و جمعیت) به صورت دستی وارد شده‌اند. در نظر بگیرید یک منبع معتبر و به روز برای این داده ها پیدا کنید.
    Map Data: The iran_geo.json file should be obtained from a trusted source of geospatial data. / داده‌های نقشه: فایل iran_geo.json باید از یک منبع قابل اعتماد داده‌های مکانی جغرافیایی به دست آید.

Future Improvements / بهبودهای آینده

Here are some ideas for improving the project: / در اینجا ایده‌هایی برای بهبود پروژه وجود دارد:

    Data Source Automation: / خودکارسازی منبع داده:
        Instead of manually entering city data, fetch it from an online API or a database. This would ensure the data is always up-to-date. / به جای وارد کردن دستی داده‌های شهر، آن را از یک API آنلاین یا یک پایگاه داده واکشی کنید. این اطمینان می‌دهد که داده‌ها همیشه به‌روز هستند.
        Example: Use the GeoNames API or similar to fetch city data. / مثال: از API GeoNames یا مشابه آن برای واکشی داده‌های شهر استفاده کنید.
    Dynamic Population Data: / داده‌های پویای جمعیت:
        Implement functionality to display population data for different years or time periods. / قابلیت نمایش داده‌های جمعیت را برای سال‌ها یا دوره‌های زمانی مختلف پیاده‌سازی کنید.
        Implementation: Store population data for multiple years in the DataFrame and allow users to select the year to display. / پیاده‌سازی: داده‌های جمعیت را برای چندین سال در DataFrame ذخیره کنید و به کاربران اجازه دهید سالی را که می‌خواهند نمایش داده شود انتخاب کنند.
    Enhanced Map Visualization: / تجسم بهبود یافته نقشه:
        Use different marker sizes or colors to represent the population of each city visually on the map. / از اندازه‌ها یا رنگ‌های مختلف نشانگر برای نمایش بصری جمعیت هر شهر روی نقشه استفاده کنید.
        Example: Marker size could be proportional to the city’s population. / مثال: اندازه نشانگر می‌تواند متناسب با جمعیت شهر باشد.
    Interactive Map Exploration: / اکتشاف تعاملی نقشه:
        Add zooming and panning capabilities to the map. / قابلیت‌های بزرگنمایی و پیمایش را به نقشه اضافه کنید.
        Implementation: Use matplotlib’s built-in zooming and panning tools or integrate a library like folium for more advanced map interactions. / پیاده‌سازی: از ابزارهای بزرگنمایی و پیمایش داخلی matplotlib استفاده کنید یا کتابخانه‌ای مانند folium را برای تعاملات نقشه پیشرفته‌تر ادغام کنید.
    Additional City Information: / اطلاعات اضافی شهر:
        Display additional information about each city (e.g., area, density, major industries) in the interactive charts or in a separate pop-up window. / اطلاعات اضافی در مورد هر شهر (به عنوان مثال، مساحت، تراکم، صنایع اصلی) را در نمودارهای تعاملی یا در یک پنجره بازشو جداگانه نمایش دهید.
        Implementation: Add more columns to the city data DataFrame and include them in the show_population function. / پیاده‌سازی: ستون‌های بیشتری را به DataFrame داده‌های شهر اضافه کنید و آنها را در تابع show_population بگنجانید.
    User Interface: / رابط کاربری:
        Create a graphical user interface (GUI) using libraries like Tkinter or PyQt to make the application more user-friendly. / یک رابط کاربری گرافیکی (GUI) با استفاده از کتابخانه‌هایی مانند Tkinter یا PyQt ایجاد کنید تا استفاده از برنامه آسان‌تر شود.
        Functionality: Could include a search bar to find cities, dropdown menus to select data layers, and options to customize the map appearance. / عملکرد: می تواند شامل یک نوار جستجو برای یافتن شهرها، منوهای کشویی برای انتخاب لایه های داده و گزینه هایی برای سفارشی کردن ظاهر نقشه باشد.
    Data Normalization / نرمال سازی داده
        Normalize the population data to enhance the color or size mapping on the map. Use normalization techniques to scale the population values to a specific range, making the visual representation more effective. / داده های جمعیت را برای بهبود رنگ یا اندازه نقشه بر روی نقشه نرمال کنید. از تکنیک های نرمال سازی برای مقیاس بندی مقادیر جمعیت به یک محدوده خاص استفاده کنید و نمایش بصری را موثرتر کنید.
    Clustering / خوشه بندی
        Implement a clustering algorithm (e.g., k-means) to group cities based on population density or geographical proximity. Display these clusters with different colors to identify regional patterns. / یک الگوریتم خوشه بندی (به عنوان مثال، k-means) را برای گروه بندی شهرها بر اساس تراکم جمعیت یا مجاورت جغرافیایی پیاده سازی کنید. این خوشه ها را با رنگ های مختلف نمایش دهید تا الگوهای منطقه ای شناسایی شوند.

License / مجوز
