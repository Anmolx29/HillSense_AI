import streamlit as st
import firebase_admin
import pandas as pd
import plotly.graph_objects as go
import json
import time

from firebase_admin import credentials
from firebase_admin import db
from streamlit_autorefresh import st_autorefresh

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="HillSense AI",
    page_icon="🌱",
    layout="wide"
)

# =====================================
# AUTO REFRESH
# =====================================

st_autorefresh(

    interval=5000,

    key="dashboardrefresh"

)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""

<style>

.main {
    background-color: #0f172a;
    color: white;
}

h1, h2, h3 {
    color: #22c55e;
}

[data-testid="metric-container"] {
    background-color: #1e293b;
    border-radius: 15px;
    padding: 15px;
    border: 1px solid #334155;
}

</style>

""", unsafe_allow_html=True)

# =====================================
# FIREBASE CONNECTION
# =====================================

if not firebase_admin._apps:

    firebase_key = json.loads(

        st.secrets["FIREBASE_KEY"]

    )

    cred = credentials.Certificate(
        firebase_key
    )

    firebase_admin.initialize_app(cred, {

        'databaseURL':
        'https://hillsenseai-default-rtdb.firebaseio.com/'

    })

# =====================================
# TITLE
# =====================================

st.title("🌱 HillSense AI Dashboard")

st.markdown(
    "### Real-Time Smart Agriculture Monitoring System"
)

# =====================================
# READ FIREBASE DATA
# =====================================

sensor_ref = db.reference('/sensor')

prediction_ref = db.reference('/prediction')

sensor_data = sensor_ref.get()

prediction_data = prediction_ref.get()

# =====================================
# HANDLE NO DATA
# =====================================

if not sensor_data:

    st.error(
        "🔴 Sensors Offline / Powered Off"
    )

    st.stop()

# =====================================
# SENSOR STATUS CHECK
# =====================================

last_seen = sensor_data.get(
    'last_seen',
    0
)

current_time = int(time.time())

time_difference = current_time - last_seen

if time_difference > 30:

    st.error(
        "🔴 Sensors Offline / Powered Off"
    )

    st.stop()

else:

    st.success(
        "🟢 Sensors Online"
    )

# =====================================
# EXTRACT SENSOR VALUES
# =====================================

temperature = float(

    sensor_data.get(
        'temperature', 0
    )

)

humidity = float(

    sensor_data.get(
        'humidity', 0
    )

)

moisture = float(

    sensor_data.get(
        'moisture', 0
    )

)

# =====================================
# EXTRACT AI PREDICTIONS
# =====================================

soil_quality = "Waiting..."

irrigation = "Waiting..."

crop = "Waiting..."

fertilizer = "Waiting..."

if prediction_data:

    soil_quality = prediction_data.get(
        'soil_quality',
        'Unknown'
    )

    irrigation = prediction_data.get(
        'irrigation',
        'Unknown'
    )

    crop = prediction_data.get(
        'crop',
        'Unknown'
    )

    fertilizer = prediction_data.get(
        'fertilizer',
        'Unknown'
    )

# =====================================
# METRICS
# =====================================

st.subheader("📡 Live Sensor Data")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "🌡 Temperature",
        f"{temperature:.1f} °C"
    )

with col2:

    st.metric(
        "💧 Humidity",
        f"{humidity:.1f} %"
    )

with col3:

    st.metric(
        "🌱 Moisture",
        f"{moisture:.1f} %"
    )

with col4:

    st.metric(
        "🤖 Soil Quality",
        soil_quality
    )

# =====================================
# STATUS SECTION
# =====================================

st.subheader("📊 Soil Status")

if moisture < 30:

    st.error(
        "⚠ Soil is very dry"
    )

elif moisture < 50:

    st.warning(
        "⚠ Soil moisture is moderate"
    )

else:

    st.success(
        "✅ Soil moisture is healthy"
    )

# =====================================
# AI RECOMMENDATIONS
# =====================================

st.subheader("🤖 Smart Recommendations")

col5, col6, col7 = st.columns(3)

with col5:

    st.info(

        f"""
        💧 Irrigation

        {irrigation}
        """
    )

with col6:

    st.success(

        f"""
        🌾 Recommended Crop

        {crop}
        """
    )

with col7:

    st.warning(

        f"""
        🧪 Fertilizer

        {fertilizer}
        """
    )

# =====================================
# CHART DATA
# =====================================

chart_data = pd.DataFrame({

    'Sensor': [
        'Temperature',
        'Humidity',
        'Moisture'
    ],

    'Value': [
        temperature,
        humidity,
        moisture
    ]

})

# =====================================
# SENSOR ANALYTICS
# =====================================

st.subheader("📈 Sensor Analytics")

fig = go.Figure(

    data=[

        go.Bar(

            x=chart_data['Sensor'],

            y=chart_data['Value']

        )
    ]
)

fig.update_layout(

    title="Live Sensor Values",

    xaxis_title="Sensors",

    yaxis_title="Values",

    height=500,

    template="plotly_dark"
)

st.plotly_chart(
    fig,
    width='stretch'
)

# =====================================
# GAUGE CHARTS
# =====================================

st.subheader("📟 Live Gauges")

g1, g2, g3 = st.columns(3)

with g1:

    temp_fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=temperature,

        title={'text': "Temperature"},

        gauge={
            'axis': {'range': [0, 50]}
        }
    ))

    st.plotly_chart(
        temp_fig,
        width='stretch'
    )

with g2:

    hum_fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=humidity,

        title={'text': "Humidity"},

        gauge={
            'axis': {'range': [0, 100]}
        }
    ))

    st.plotly_chart(
        hum_fig,
        width='stretch'
    )

with g3:

    moist_fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=moisture,

        title={'text': "Moisture"},

        gauge={
            'axis': {'range': [0, 100]}
        }
    ))

    st.plotly_chart(
        moist_fig,
        width='stretch'
    )

# =====================================
# RAW FIREBASE DATA
# =====================================

st.subheader("🗂 Firebase Data")

st.json({

    'sensor': sensor_data,

    'prediction': prediction_data

})

# =====================================
# FOOTER
# =====================================

st.markdown("---")

st.caption(
    "🌱 HillSense AI • Real-Time IoT Smart Agriculture System"
)