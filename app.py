import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = "data.csv"


@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    data.drop(data.index[data['LATITUDE'] == 0], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data


data = load_data(100000)
original = data

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used"
            "to analyze motor collisions in NYC")

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 27)

midpoint = (np.average(data['latitude']), np.average(data['longitude']))
injured_data = data.query("`number of persons injured` >= @injured_people")
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 9
    },
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=injured_data[['accident date', 'accident time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            auto_highlight=True,
            get_radius=250,
            get_fill_color='[229, 0, 0, 140]',
            pickable=True
        ),
    ],
))

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[pd.to_datetime(data['accident time']).dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['accident date', 'accident time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))

filtered = data[
    (pd.to_datetime(data['accident time']).dt.hour >= hour) & (
                pd.to_datetime(data['accident time']).dt.hour < (hour + 1))
    ]
hist = np.histogram(pd.to_datetime(filtered['accident time']).dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])
if select == 'Pedestrians':
    st.write(original.query('`number of pedestrians injured` >= 1')[
                 ['on street name', 'number of pedestrians injured']].sort_values(by=['number of pedestrians injured'],
                                                                                  ascending=False).dropna(how='any')[
             :5])
elif select == 'Cyclists':
    st.write(
        original.query('`number of cyclist injured` >= 1')[['on street name', 'number of cyclist injured']].sort_values(
            by=['number of cyclist injured'], ascending=False).dropna(how='any')[:5])
elif select == 'Motorists':
    st.write(original.query('`number of motorist injured` >= 1')[
                 ['on street name', 'number of motorist injured']].sort_values(by=['number of motorist injured'],
                                                                               ascending=False).dropna(how='any')[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
