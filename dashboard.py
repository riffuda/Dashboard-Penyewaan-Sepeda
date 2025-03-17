import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Load dataset
day_update = pd.read_csv("day_update.csv")
hour_update = pd.read_csv("hour_update.csv")

# Konversi kolom tanggal ke datetime
day_update["dteday"] = pd.to_datetime(day_update["dteday"])
hour_update["date"] = pd.to_datetime(hour_update["date"])

# Tambahkan gambar sebagai header
st.image("image.jpg", use_container_width=True)

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Data")

# Pilih Rentang Tanggal dengan Date Input
min_date = day_update["dteday"].min()
max_date = day_update["dteday"].max()

# Konversi ke format datetime.date untuk slider
min_date = min_date.date()
max_date = max_date.date()

# Pilih Rentang Tanggal dengan Slider
selected_date_range = st.sidebar.slider(
    "Pilih Rentang Tanggal",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Konversi kembali ke datetime untuk filter
start_date, end_date = pd.to_datetime(selected_date_range)

# Konversi input tanggal ke datetime
start_date, end_date = map(pd.to_datetime, selected_date_range)

# Filter dataset berdasarkan rentang tanggal
day_update = day_update[(day_update["dteday"] >= start_date) & (day_update["dteday"] <= end_date)]
hour_update = hour_update[(hour_update["date"] >= start_date) & (hour_update["date"] <= end_date)]

# --- VISUALISASI --- 
st.header("Analisis Penyewaan Sepeda")

## Tren Penyewaan Sepeda Harian
st.subheader("Tren Penyewaan Sepeda Harian")

fig, ax = plt.subplots(figsize=(14, 6))
sns.lineplot(data=day_update, x="dteday", y="cnt", color="royalblue", linewidth=2)
ax.set_xlabel("Tanggal", fontsize=12, fontweight="bold")
ax.set_ylabel("Jumlah Penyewaan", fontsize=12, fontweight="bold")
ax.set_title("Tren Penyewaan Sepeda Harian", fontsize=14, fontweight="bold", color="darkblue")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.6)
st.pyplot(fig)

# Tren Penyewaan Sepeda Bulanan
st.subheader("Tren Penyewaan Sepeda Bulanan")

monthly_counts = hour_update.groupby(hour_update["date"].dt.to_period("M"))["total_rentals"].sum()
monthly_counts.index = monthly_counts.index.to_timestamp()

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x=monthly_counts.index, y=monthly_counts.values, marker="o", linewidth=2, color="#1976D2")

for i, (x, y) in enumerate(zip(monthly_counts.index, monthly_counts.values)):
    if i % 2 == 0:
        offset = -(y * 0.05)
        plt.text(x, y + offset, f"{int(y):,}", ha="center", fontsize=9, color="black", bbox=dict(facecolor="white", edgecolor="none", alpha=0.7))

plt.xlabel("Bulan", fontsize=11)
plt.ylabel("Jumlah Peminjaman", fontsize=11)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.xticks(rotation=45)
plt.title("Tren Penyewaan Sepeda per Bulan", fontsize=14, fontweight="bold", color="#0D47A1", pad=20)
st.pyplot(fig)

## Total Penyewaan Sepeda Berdasarkan Musim
st.subheader("Total Bike Rentals by Season")

fig, ax = plt.subplots(figsize=(8,6))
sns.barplot(
    data=hour_update, 
    x="season", 
    y="total_rentals", 
    estimator=sum, 
    hue="season",  
    dodge=False,   
    legend=False,  
    palette="Set2"
)

ax.set_title("Total Penyewaan Sepeda Berdasarkan Musim", fontsize=12, fontweight="bold")
ax.set_xlabel("Season")
ax.set_ylabel("Total Rentals")
ax.grid(axis="y", linestyle="--", alpha=0.5)
st.pyplot(fig)

## Top 5 dan Bottom 5 Jam dengan Penyewaan Sepeda Tertinggi
st.subheader("Jam dengan Paling Banyak & Paling Sedikit Penyewa Sepeda")

sum_order_items_df = hour_update.groupby("hour")["total_rentals"].sum().reset_index()
top_5 = sum_order_items_df.nlargest(5, "total_rentals").sort_values(by="total_rentals", ascending=False)
bottom_5 = sum_order_items_df.nsmallest(5, "total_rentals").sort_values(by="total_rentals", ascending=True)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 10))

# Penyewa terbanyak
sns.barplot(x="hour", y="total_rentals", hue="hour", data=top_5, dodge=False, legend=False, palette=["#FFA07A", "#FFA07A", "#FF4500", "#FFA07A", "#FFA07A"], ax=ax[0])
ax[0].set_xlabel("Hour of the Day (PM)", fontsize=20)
ax[0].set_title("Top 5 Jam Paling Banyak Penyewa Sepeda", loc="center", fontsize=20)
ax[0].tick_params(axis="x", labelsize=15)
ax[0].grid(axis="y", linestyle="--", alpha=0.5)

# Penyewa tersedikit
sns.barplot(x="hour", y="total_rentals", hue="hour", data=bottom_5, dodge=False, legend=False, palette=["#4682B4", "#4682B4", "#4682B4", "#00008B", "#4682B4"], ax=ax[1])
ax[1].set_xlabel("Hour of the Day (AM)", fontsize=20)
ax[1].set_title("Top 5 Jam Paling Sedikit Penyewa Sepeda", loc="center", fontsize=20)
ax[1].tick_params(axis="x", labelsize=15)
ax[1].grid(axis="y", linestyle="--", alpha=0.5)

st.pyplot(fig)

## Kategori Peminjaman Sepeda
st.subheader("Kategori Peminjaman Sepeda Berdasarkan Musim")

def categorize_rentals(rentals):
    if rentals < 100:
        return "Rendah"
    elif 100 <= rentals <= 300:
        return "Sedang"
    else:
        return "Tinggi"

hour_update["rental_category"] = hour_update["total_rentals"].apply(categorize_rentals)
season_distribution = hour_update.groupby(["season", "rental_category"])["total_rentals"].count().unstack()

if not season_distribution.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    season_distribution.plot(kind="bar", stacked=True, colormap="viridis", ax=ax)
    ax.set_xlabel("Musim")
    ax.set_ylabel("Jumlah Peminjaman")
    ax.set_title("Distribusi Peminjaman Berdasarkan Musim")
    ax.legend(title="Kategori Peminjaman")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig)
else:
    st.warning("Tidak ada data untuk ditampilkan dalam grafik ini.")
