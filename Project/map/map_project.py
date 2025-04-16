import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import mplcursors

# Given ten big cities
cities_data = pd.DataFrame({
    'City': ['Tehran', 'Mashhad', 'Isfahan', 'Karaj', 'Shiraz',
             'Tabriz', 'Qom', 'Ahvaz', 'Kermanshah', 'Urmia'],
    'Latitude': [35.6892, 36.2605, 32.6539, 35.8327, 29.5918,
                 38.0962, 34.6416, 31.3203, 34.3142, 37.5553],
    'Longitude': [51.3890, 59.6168, 51.6660, 50.9916, 52.5836,
                  46.2738, 50.8746, 48.6691, 47.0650, 45.0725],
    'Population': [8847000, 3074000, 2043000, 1963000, 1565000,
                   1558000, 1230000, 1185000, 946000, 736000]})


#Loading the map of Iran ( بارگذاری نقشه ایران)
iran = gpd.read_file("iran_geo.json")

# Drawing a map of Iran(رسم نقشه ایران)
fig, ax = plt.subplots(figsize=(10, 8))
iran.plot(ax=ax, color='beige', edgecolor='black')

# Points of cities(نقاط شهرها)
scatter = ax.scatter(cities_data['Longitude'],
                    cities_data['Latitude'],
                    s=100,
                    color='skyblue',
                    zorder=5)

# Initial label of cities(برچسب اولیه شهرها)
labels = []
for i, row in cities_data.iterrows():
    label = ax.text(row['Longitude'] + 0.3, row['Latitude'],
                    row['City'], fontsize=9, zorder=6)
    labels.append(label)
ax.set_title('Top 10 Most Populated Cities in Iran')
ax.set_xlabel('Longitude') #طول جغرافیایی
ax.set_ylabel('Latitude') #عرض جغرافیایی

# Population graph display function(تابع نمایش نمودار جمعیت)
def show_population(index):
    city = cities_data.iloc[index]

    # Temporary change of city name color and size(تغییر موقت رنگ و اندازه نام شهر)
    labels[index].set_color('red')
    labels[index].set_fontsize(12)
    fig.canvas.draw_idle()

    # Population chart(نمودار جمعیت)
    plt.figure(figsize=(4, 3))
    plt.bar(city['City'], city['Population'], color='green')
    plt.title(f"Population of {city['City']}")
    plt.ylabel("Population")
    plt.tight_layout()
    plt.show()

    # Restore previous color(بازگرداندن رنگ قبلی)
    labels[index].set_color('black')
    labels[index].set_fontsize(9)
    fig.canvas.draw_idle()

# Click interaction(تعامل با کلیک)
cursor = mplcursors.cursor(scatter, hover=False)
@cursor.connect("add")
def on_click(sel):
    show_population(sel.index)

plt.show()