import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Market Trends Dashboard", layout="wide")

# Load Data
df = pd.read_csv(r"E:\Market Trends Visualization\market_trends.csv", parse_dates=["Date"])

df["date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# Sidebar Filters
st.sidebar.header("Filters")
tickers = st.sidebar.multiselect("Select Stocks", df["Ticker"].unique(), default=df["Ticker"].unique()[:5])
sector = st.sidebar.selectbox("Select Sector", ["All"] + sorted(df["Sector"].unique()))
year = st.sidebar.selectbox("Select Year", sorted(df["Year"].unique()))

# Apply Filters
filtered_df = df[df["Ticker"].isin(tickers)]
if sector != "All":
    filtered_df = filtered_df[filtered_df["Sector"] == sector]
filtered_df = filtered_df[filtered_df["Year"] == year]

st.title("📊 Market Trends Dashboard")

# -----------------------------
# 1. Sector-wise Performance
# -----------------------------
st.subheader("📌 Sector-wise Performance")

sector_perf = df.groupby("Sector")["Yearly_Return"].mean().reset_index()

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(data=sector_perf, x="Sector", y="Yearly_Return", palette="Blues_r")
plt.xticks(rotation=45)
st.pyplot(fig)

# -----------------------------
# 2. Cumulative Return
# -----------------------------
st.subheader("📌 Cumulative Return Over Time")

df["Daily_Return"] = df.groupby("Ticker")["Close"].pct_change()
df["Cumulative_Return"] = (1 + df["Daily_Return"]).groupby(df["Ticker"]).cumprod() - 1

fig, ax = plt.subplots(figsize=(12,5))
for t in tickers:
    temp = df[df["Ticker"] == t]
    plt.plot(temp["date"], temp["Cumulative_Return"], label=t)

plt.legend()
plt.title("Cumulative Return Over Time")
st.pyplot(fig)

# -----------------------------
# 3. Volatility View
# -----------------------------
st.subheader("📌 Volatility (Risk Indicator)")

vol_df = df.groupby("Ticker")["Daily_Return"].std().reset_index(name="Volatility")

fig, ax = plt.subplots(figsize=(12,5))
sns.barplot(data=vol_df.sort_values("Volatility", ascending=False),
            x="Ticker", y="Volatility", palette="Reds")
plt.xticks(rotation=90)
st.pyplot(fig)

# -----------------------------
# 4. Correlation Heatmap
# -----------------------------
st.subheader("📌 Stock Price Correlation Heatmap")

pivot = df.pivot_table(index="date", columns="Ticker", values="Close")
corr = pivot.pct_change().corr()

fig, ax = plt.subplots(figsize=(14,10))
sns.heatmap(corr, cmap="coolwarm", linewidths=0.5)
st.pyplot(fig)

# -----------------------------
# 5. Monthly Top Gainers & Losers
# -----------------------------
st.subheader("📌 Monthly Top 5 Gainers & Losers")

monthly = (
    df.groupby(["Year", "Month", "Ticker"])["Close"]
      .agg(["first", "last"])
      .reset_index()
)
monthly["Monthly_Return"] = (monthly["last"] / monthly["first"]) - 1

year_months = sorted(monthly[monthly["Year"] == year]["Month"].unique())

for m in year_months:
    st.write(f"### Month: {m}")

    month_data = monthly[(monthly["Year"] == year) & (monthly["Month"] == m)]

    gainers = month_data.sort_values("Monthly_Return", ascending=False).head(5)
    losers = month_data.sort_values("Monthly_Return").head(5)

    col1, col2 = st.columns(2)

    with col1:
        st.write("#### Top 5 Gainers")
        fig, ax = plt.subplots()
        sns.barplot(data=gainers, x="Monthly_Return", y="Ticker", palette="Greens_r")
        st.pyplot(fig)

    with col2:
        st.write("#### Top 5 Losers")
        fig, ax = plt.subplots()
        sns.barplot(data=losers, x="Monthly_Return", y="Ticker", palette="Reds_r")
        st.pyplot(fig)

# ==============================
# KPI FILTERS (Independent)
# ==============================
st.sidebar.header("📌 KPI Filters")

# Sector filter for KPIs
kpi_sector = st.sidebar.selectbox(
    "Select Sector for KPIs",
    ["All"] + sorted(df["Sector"].unique())
)

# Filter 1: Average Price
price_filter = st.sidebar.multiselect(
    "Select Stocks for Average Price",
    df["Ticker"].unique(),
    default=df["Ticker"].unique()
)

# Filter 2: Average Volume
volume_filter = st.sidebar.multiselect(
    "Select Stocks for Average Volume",
    df["Ticker"].unique(),
    default=df["Ticker"].unique()
)

# Filter 3: Market Summary (Green vs Red)
summary_filter = st.sidebar.multiselect(
    "Select Stocks for Market Summary",
    df["Ticker"].unique(),
    default=df["Ticker"].unique()
)

#Apply Sector Filter to KPI Data

kpi_df = df.copy()
if kpi_sector != "All":
    kpi_df = kpi_df[kpi_df["Sector"] == kpi_sector]

#Compute KPI Metrics

# 1. Average Price
avg_price = kpi_df[kpi_df["Ticker"].isin(price_filter)]["Close"].mean()

# 2. Average Volume
avg_volume = kpi_df[kpi_df["Ticker"].isin(volume_filter)]["Volume"].mean()

# 3. Market Summary (Green vs Red)
summary_df = kpi_df[kpi_df["Ticker"].isin(summary_filter)]
green_count = (summary_df["Yearly_Return"] > 0).sum()
red_count = (summary_df["Yearly_Return"] < 0).sum()

#Display Color‑Coded KPI Cards
# ==============================
# KPI SECTION
# ==============================
st.subheader("📌 Market Summary KPIs")

col1, col2, col3 = st.columns(3)

# Color logic
price_color = "green" if avg_price > 0 else "red"
volume_color = "green" if avg_volume > df["Volume"].mean() else "red"
summary_color = "green" if green_count > red_count else "red"

with col1:
    st.markdown(f"""
        <div style="padding:15px; border-radius:10px; background-color:#f0f0f0;">
            <h4>Average Price</h4>
            <h2 style="color:{price_color};">₹ {avg_price:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style="padding:15px; border-radius:10px; background-color:#f0f0f0;">
            <h4>Average Volume</h4>
            <h2 style="color:{volume_color};">{avg_volume:,.0f}</h2>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style="padding:15px; border-radius:10px; background-color:#f0f0f0;">
            <h4>Green vs Red Stocks</h4>
            <h2 style="color:{summary_color};">{green_count} Green / {red_count} Red</h2>
        </div>
    """, unsafe_allow_html=True)


# -----------------------------
# 6. Top 10 Green & Red Stocks
# -----------------------------
st.subheader("📌 Top 10 Green & Red Stocks (Yearly Performance)")

# Compute yearly return per stock
yearly_perf = df.groupby("Ticker")["Yearly_Return"].mean().reset_index()

# Top 10 Green (Best Performers)
top10_green = yearly_perf.sort_values("Yearly_Return", ascending=False).head(10)

# Top 10 Red (Worst Performers)
top10_red = yearly_perf.sort_values("Yearly_Return").head(10)

col1, col2 = st.columns(2)

with col1:
    st.write("### 🟢 Top 10 Green Stocks (Best Performers)")
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(data=top10_green, x="Yearly_Return", y="Ticker", palette="Greens_r")
    plt.title("Top 10 Green Stocks")
    st.pyplot(fig)

with col2:
    st.write("### 🔴 Top 10 Red Stocks (Worst Performers)")
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(data=top10_red, x="Yearly_Return", y="Ticker", palette="Reds_r")
    plt.title("Top 10 Red Stocks")
    st.pyplot(fig)
