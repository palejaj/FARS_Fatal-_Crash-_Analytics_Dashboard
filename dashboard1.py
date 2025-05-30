import streamlit as st
import pandas as pd
import plotly.express as px
import us
from sklearn.linear_model import LinearRegression
import numpy as np
import gdown
import os

# === Download CSVs from Google Drive ===
accident_url = "https://drive.google.com/uc?id=1i8dlbEbTazDE0eJ2hbZEkuvunssiF9Yl"
person_url = "https://drive.google.com/uc?id=1pKdyOsaFFrNClSpE4nM2j11Ro6NRC0CH"
drugs_url = "https://drive.google.com/uc?id=1LWMRUnRXt2jTFtQbAImErBPrFJgRl169"

if not os.path.exists("accidents_filtered.csv"):
    gdown.download(accident_url, "accidents_filtered.csv", quiet=False)

if not os.path.exists("person_filtered.csv"):
    gdown.download(person_url, "person_filtered.csv", quiet=False)

if not os.path.exists("drugs_filtered.csv"):
    gdown.download(drugs_url, "drugs_filtered.csv", quiet=False)

@st.cache_data(show_spinner=True)
def load_data():
    accident_df = pd.read_csv("accidents_filtered.csv")
    person_df = pd.read_csv("person_filtered.csv")
    drugs_df = pd.read_csv("drugs_filtered.csv")
    return accident_df, person_df, drugs_df

accident_df, person_df, drugs_df = load_data()

# === Sidebar Filters ===
st.sidebar.header("Filter Options")
years = sorted(accident_df["YEAR"].unique())
states = sorted(accident_df["STATENAME"].dropna().unique())
selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
selected_states = st.sidebar.multiselect("Select State(s)", states, default=states)

# Filter data
accident_df_filtered = accident_df[
    (accident_df["YEAR"].isin(selected_years)) & (accident_df["STATENAME"].isin(selected_states))
]
person_df_filtered = person_df[person_df["YEAR"].isin(selected_years)]
drugs_df_filtered = drugs_df[drugs_df["YEAR"].isin(selected_years)]

# === Dashboard ===
st.title("🚗 FARS Crash Data Dashboard (2008–2023)")

# Yearly Summary
st.subheader("📊 Yearly Crash Trends")
yearly_summary = (
    accident_df.groupby("YEAR")["ST_CASE"].nunique().reset_index(name="Accidents")
    .merge(person_df.groupby("YEAR")["ST_CASE"].nunique().reset_index(name="People_Involved"), on="YEAR")
    .merge(drugs_df.groupby("YEAR")["ST_CASE"].nunique().reset_index(name="Drug_Cases"), on="YEAR", how="left")
    .fillna(0)
)
melted = yearly_summary.melt(id_vars="YEAR", var_name="Category", value_name="Count")
fig = px.bar(melted, x="YEAR", y="Count", color="Category", barmode="group", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# Compare Two Years
st.subheader("📆 Compare Two Years Side-by-Side")
col1, col2 = st.columns(2)
with col1:
    year_a = st.selectbox("Select Year A", years, index=years.index(2022))
with col2:
    year_b = st.selectbox("Select Year B", years, index=years.index(2023))

summary_compare = pd.DataFrame({
    "Category": ["Accidents", "People Involved", "Drug-Involved"],
    "Year A": [
        accident_df[accident_df["YEAR"] == year_a]["ST_CASE"].nunique(),
        person_df[person_df["YEAR"] == year_a]["ST_CASE"].nunique(),
        drugs_df[drugs_df["YEAR"] == year_a]["ST_CASE"].nunique()
    ],
    "Year B": [
        accident_df[accident_df["YEAR"] == year_b]["ST_CASE"].nunique(),
        person_df[person_df["YEAR"] == year_b]["ST_CASE"].nunique(),
        drugs_df[drugs_df["YEAR"] == year_b]["ST_CASE"].nunique()
    ]
})
fig = px.bar(summary_compare.melt(id_vars="Category", var_name="Year", value_name="Count"),
             x="Category", y="Count", color="Year", barmode="group",
             title=f"Crash Metrics: {year_a} vs {year_b}", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# Weather Conditions
st.subheader("🌦️ Crashes by Weather Conditions")
weather_df = accident_df_filtered["WEATHER1NAME"].value_counts().reset_index()
weather_df.columns = ["Weather", "Crash Count"]
fig = px.bar(weather_df.head(10), x="Crash Count", y="Weather", orientation="h", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# Light Conditions
st.subheader("💡 Light Conditions Impact")
fig = px.pie(accident_df_filtered, names="LGT_CONDNAME", template="plotly_white", hole=0.4)
fig.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig, use_container_width=True)

# Age vs Gender Heatmap
st.subheader("🧑‍🤝‍🧑 Heatmap of Age vs Gender")
age_gender_df = person_df_filtered[
    (person_df_filtered["SEXNAME"].isin(["Male", "Female"])) & (person_df_filtered["AGE"].between(0, 100))
]
heat_df = age_gender_df.groupby(["AGE", "SEXNAME"]).size().reset_index(name="Count")
fig = px.density_heatmap(heat_df, x="AGE", y="SEXNAME", z="Count", color_continuous_scale="Reds", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# Urban vs Rural
st.subheader("🏙️ Urban vs Rural Crash Comparison")
area_df = accident_df_filtered["RUR_URBNAME"].value_counts().reset_index()
area_df.columns = ["Area Type", "Crash Count"]
fig = px.pie(area_df, names="Area Type", values="Crash Count", template="plotly_white", hole=0.4)
st.plotly_chart(fig, use_container_width=True)

# Animated Geospatial Map
st.subheader("🌍 Animated Geospatial Crash Map (Year-wise)")
geo_df = accident_df[
    (accident_df["LATITUDE"].between(20, 50)) & (accident_df["LONGITUD"].between(-130, -60))
].dropna(subset=["LATITUDE", "LONGITUD"])
fig = px.scatter_mapbox(
    geo_df, lat="LATITUDE", lon="LONGITUD",
    animation_frame="YEAR", zoom=3.5,
    mapbox_style="carto-positron", height=500
)
st.plotly_chart(fig, use_container_width=True)

# Zoomable City Map
st.subheader("🏙️ Zoomable City-Level Crash Map")
selected_city = st.selectbox("Select a City", sorted(accident_df_filtered["CITYNAME"].dropna().unique()))
city_map_df = accident_df_filtered[accident_df_filtered["CITYNAME"] == selected_city].dropna(subset=["LATITUDE", "LONGITUD"])
fig = px.scatter_mapbox(city_map_df, lat="LATITUDE", lon="LONGITUD", zoom=10,
                        mapbox_style="carto-positron", height=400)
st.plotly_chart(fig, use_container_width=True)

# Fatality Choropleth
st.subheader("☠️ Fatality Rate by State (2008–2023)")
state_stats = (
    accident_df.groupby("STATENAME")[["ST_CASE", "FATALS"]]
    .agg({"ST_CASE": "nunique", "FATALS": "sum"})
    .reset_index()
)
state_stats["Fatality Rate (%)"] = (state_stats["FATALS"] / state_stats["ST_CASE"]) * 100
state_stats["state_abbr"] = state_stats["STATENAME"].apply(lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else None)
state_stats = state_stats.dropna()
fig = px.choropleth(state_stats, locations="state_abbr", locationmode="USA-states",
                    color="Fatality Rate (%)", scope="usa", color_continuous_scale="OrRd",
                    title="Average Fatality Rate by State (2008–2023)",
                    labels={"Fatality Rate (%)": "Fatality %"}, template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# Fatality Forecast
st.subheader("📈 Fatality Trend Forecast")
fatal_years = accident_df.groupby("YEAR")["FATALS"].sum().reset_index()
X = fatal_years["YEAR"].values.reshape(-1, 1)
y = fatal_years["FATALS"].values
model = LinearRegression().fit(X, y)
future_years = np.arange(2024, 2028).reshape(-1, 1)
preds = model.predict(future_years)
forecast_df = pd.DataFrame({
    "YEAR": list(fatal_years["YEAR"]) + future_years.flatten().tolist(),
    "FATALS": list(fatal_years["FATALS"]) + preds.tolist(),
    "Type": ["Actual"] * len(y) + ["Forecast"] * len(preds)
})
fig = px.line(forecast_df, x="YEAR", y="FATALS", color="Type",
              title="Total Fatalities and Forecast (2024–2027)", markers=True, template="plotly_white")
st.plotly_chart(fig, use_container_width=True)
