import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 읽기
file_path = '/workspaces/Graph/dummy_data_241018.csv'
try:
    df = pd.read_csv(file_path, on_bad_lines='skip')
except pd.errors.ParserError:
    st.error("There was an error reading the CSV file. Please check the file format.")
    df = pd.DataFrame()

# 데이터가 비어있지 않은 경우에만 실행
if not df.empty:
    # 날짜 형식 변환
    df['event_time'] = pd.to_datetime(df['event_time'], errors='coerce')
    df = df.dropna(subset=['event_time'])

    # Streamlit 앱 만들기
    st.title("Device Fault Analysis")
    st.sidebar.header("Filter Options")

    # Device, Vendor, Role 선택 옵션 생성
    devices = ['All'] + list(df['device_name'].unique())
    vendors = ['All'] + list(df['vendor'].unique())
    roles = ['All'] + list(df['role'].unique())

    selected_device = st.sidebar.selectbox("Device Name", devices)
    selected_vendor = st.sidebar.selectbox("Vendor", vendors)
    selected_role = st.sidebar.selectbox("Role", roles)

    # 날짜 범위 선택
    date_range = st.sidebar.date_input("Select Date Range", [])

    # 선택한 device, vendor, role 및 날짜 범위에 대한 데이터 필터링
    filtered_df = df
    if selected_device != 'All':
        filtered_df = filtered_df[filtered_df['device_name'] == selected_device]
    if selected_vendor != 'All':
        filtered_df = filtered_df[filtered_df['vendor'] == selected_vendor]
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df['role'] == selected_role]

    # 날짜 범위 필터링
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['event_time'] >= pd.Timestamp(start_date)) &
                                  (filtered_df['event_time'] <= pd.Timestamp(end_date))]

    # event_time을 기준으로 월단위로 고장 수 집계
    filtered_df['event_month'] = filtered_df['event_time'].dt.to_period('M')
    fault_count = filtered_df.groupby('event_month').size()

    # 시계열 그래프 그리기
    st.write(f"Recent Fault Counts for {selected_device} - {selected_vendor} - {selected_role}")
    plt.figure(figsize=(10, 5))
    plt.plot(fault_count.index.astype(str), fault_count.values, marker='o')
    plt.xlabel('Month')
    plt.ylabel('Fault Count')
    plt.title(f'Fault Count Over Time for {selected_device} ({selected_vendor}, {selected_role})')
    plt.grid(True)

    # 각 데이터 포인트에 값 표시
    for x, y in zip(fault_count.index.astype(str), fault_count.values):
        plt.text(x, y, str(y), fontsize=9, ha='center', va='bottom')

    st.pyplot(plt)
