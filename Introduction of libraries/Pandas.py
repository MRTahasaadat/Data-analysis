# Download
# pip install pandas

import pandas as pd

# Series
series = pd.Series([10, 20, 30, 40, 50], index=['a', 'b', 'c', 'd', 'e'])
print(series)#=> a    10 b    20 c    30 d    40 e    50 dtype: int64
print(series['c'])  #=>30(Access by tag)
print(series[2])  #=>30(Access with index)

# DataFrame integration
df1 = pd.DataFrame({'key': ['A', 'B'], 'value': [1, 2]})
df2 = pd.DataFrame({'key': ['A', 'B'], 'value': [3, 4]})
merged_df = pd.merge(df1, df2, on='key')

# Creating a dataset
data = {'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, 30, 28, 22],
        'City': ['New York', 'London', 'Paris', 'Tokyo']}

df = pd.DataFrame(data)
print(df)
# =>
#       Name  Age      City
# 0    Alice   25  New York
# 1      Bob   30    London
# 2  Charlie   28     Paris
# 3    David   22     Tokyo

# Accessing a row with a label(دسترسی به ردیف با برچسب)
first_row = df.loc[0]  # [Name: Alice, Age: 25, Salary: 50000]

# (دسترسی به ردیف با ایندکس)Accessing a row with an index
second_row = df.iloc[1]  # [Name: Bob, Age: 30, Salary: 60000]

# Access a column(دسترسی به یک ستون)
age_column = df['Age']  # [25, 30, 35]

# Read from CSV file
df_csv = pd.read_csv('data.csv')

# Reading from Excel file
df_excel = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# Write to CSV file
df.to_csv('output.csv', index=False)  # index=False برای عدم نوشتن اندیس

# Write in Excel file
df.to_excel('output.xlsx', sheet_name='Sheet1', index=False)

# Data cleaning and preparation

# Check for missing values
print(df.isnull().sum())
# => Number of missing values in each column
# Name    0
# Age     0
# City    0
# dtype: int64

# Delete rows with missing values
df_dropna = df.dropna()

# Fill missing values with a specific value (0)
df_fillna = df.fillna(0)

# Filling in missing values with column averages
df['Age'].fillna(df['Age'].mean(), inplace=True)

# Delete column
df_dropcolumn = df.drop('City', axis=1)

# Rename the column
df_rename = df.rename(columns={'Name': 'Full Name'})

# Data manipulation and transformation

#Filter rows(فیلتر کردن سطرها)
df_filtered = df[df['Age'] > 25]

# Sorting rows(مرتب‌سازی سطرها)
df_sorted = df.sort_values('Age', ascending=False)

# Data grouping(گروه‌بندی داده‌ها)
df_grouped = df.groupby('City')['Age'].mean()

# Add new column(اضافه کردن ستون جدید)
df['Salary'] = [50000, 60000, 55000, 45000]

# Applying a function to a column(اعمال یک تابع روی ستون)
def increase_age(age):
    return age + 1

df['Age'] = df['Age'].apply(increase_age)

# Data analysis

# Calculate descriptive statistics(محاسبه آمار توصیفی)
print(df.describe())

# Calculate descriptive statistics(محاسبه همبستگی بین ستون‌ها)
print(df.corr())

# Counting the number of unique values in a column(محاسبه تعداد مقادیر منحصربه‌فرد در یک ستون)
print(df['City'].value_counts())
