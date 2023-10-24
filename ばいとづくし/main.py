import pandas as pd 
import altair as alt
import streamlit as st
import matplotlib.pyplot as plt
import japanize_matplotlib
import seaborn as sns
import sqlite3
from cachetools import LRUCache
import math

# SQLiteデータベースに接続
conn = sqlite3.connect('income_expense.db')
cursor = conn.cursor()

# テーブルが存在しない場合は作成
cursor.execute('''CREATE TABLE IF NOT EXISTS income_expense (
                    month INTEGER PRIMARY KEY,
                    income INTEGER
                )''')
conn.commit()

# Streamlitアプリケーションが起動されるたびにデータベースをクリア
if 'started' not in st.session_state:
    cursor.execute("DELETE FROM income_expense")
    conn.commit()
    st.session_state.started = True  # セッション状態を設定

def main():

    user_type_list = {
        "配偶者控除(103万円)": 1030000,
        "社会保険加入(106万円)": 1060000,
        "扶養外(130万円)": 1300000,
        "配偶者特別控除(150万円)": 1500000,
        "配偶者特別控除上限(201万円)": 2010000
    }

    st.title('バイトづくし')

    salary_per_hour = st.number_input('時給', min_value=800.0, max_value=10000000.0, value=1000.0, step=100.0)
    day_worktime = st.number_input('１日の勤務時間', min_value=1.0, max_value=24.0, value=4.0, step=0.5)
    month = st.number_input('何月', min_value=1.0, max_value=12.0, value=1.0, step=1.0)

    selected_type = st.selectbox('年収目標を選んでください:', list(user_type_list.keys()))
    border = user_type_list[selected_type]

    income = st.number_input('今月の収入を教えてください', min_value=0, max_value=10000000)
    # border -= income
    # income_sum += income

    # フォームから月と収入情報を受け取る
    income_input = income
    month_input = month

    # データベースに月と収入情報を格納
    if st.button('データを保存'):
        cursor.execute("INSERT INTO income_expense (month, income) VALUES (?, ?)", (month_input, income_input))
        conn.commit()

    # データベースからデータを取得
    df = pd.read_sql_query("SELECT * FROM income_expense", conn)
    st.write(df)
    income_sum = df['income'].sum()

    can_work = (border - income_sum) / salary_per_hour
    st.write("残り", can_work, "時間働けます")

    left_day = can_work / day_worktime
    leftmonth = 12 - month
    if leftmonth == 0:
        st.write('月当たり', left_day, '日働ける')
    else:
        st.write('月当たり', left_day / leftmonth, '日働ける')
    st.write('月当たり',math.floor(left_day / leftmonth),'日まで働くと超えない')  
    st.write('月当たり',math.floor((border - income_sum)/leftmonth),'円まで稼ぐと超えない')
        
    plt.figure(figsize=(10, 6))
    bottom = 0
    for label, income in zip(df['month'], df['income']):
        label_str = str(label)  # ラベルを文字列に変換
        if label_str.isdigit():
            continue  # 整数のラベルは凡例に含めない
        plt.bar('合計', income, bottom=bottom, label=label_str, width=0.3)
        bottom += income

    plt.xlabel('月')
    plt.ylabel('収入')
    plt.title('月ごとの収入の積み上げ帯グラフ')

    # 103万円のメモリを追加
    plt.axhline(1030000, color='red', linestyle='--', linewidth=1, label='103万円上限')  # 103万円の水平線を追加

    # 凡例を表示
    plt.legend(loc='upper left')

    # y軸のラベルの表示形式を設定
    plt.ticklabel_format(axis='y', style='plain')

    # Streamlitにプロットを表示
    st.pyplot(plt)



if __name__ == "__main__":
    main()