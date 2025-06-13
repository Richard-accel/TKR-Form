import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TKR Intra-Op Dashboard", layout="wide")

st.title("🛠️ TKR Intra-Operative Dashboard")

# --- Load Data ---
uploaded_file = st.file_uploader("Upload exported CSV (IntraOp Data)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # --- Blood Loss ---
    st.subheader("💉 Blood Loss")
    fig = px.histogram(df, x="blood_loss", nbins=10, title="Blood Loss Distribution (mL)")
    fig.update_traces(marker_line_color="black", marker_line_width=1)
    st.plotly_chart(fig, use_container_width=True)

    # --- Complications ---
    st.subheader("⚠️ Complications")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(df["surgical_complications"].value_counts().rename_axis("Surgical Complications").reset_index(name="Count"),
                     x="Surgical Complications", y="Count", title="Surgical Complications")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(df["anaesthetic_complications"].value_counts().rename_axis("Anaesthetic Complications").reset_index(name="Count"),
                     x="Anaesthetic Complications", y="Count", title="Anaesthetic Complications")
        st.plotly_chart(fig, use_container_width=True)

    # --- Medications ---
    st.subheader("💊 Medications Administered")
    med_cols = ["prophylactic_antibiotics", "pain_management", "anticoagulants"]
    meds_df = df[med_cols].apply(lambda col: col.value_counts()).T
    meds_df.columns = [str(c) for c in meds_df.columns]
    st.bar_chart(meds_df["True"] if "True" in meds_df.columns else meds_df)

    # --- Surgical Technique ---
    st.subheader("🔧 Surgical Technique")
    tech_cols = ["traditional_surgery", "minimally_invasive", "proper_alignment_prosthesis"]
    tech_df = df[tech_cols].apply(lambda col: col.value_counts()).T
    tech_df.columns = [str(c) for c in tech_df.columns]
    st.bar_chart(tech_df["True"] if "True" in tech_df.columns else tech_df)

    # --- Navigation System and Implants ---
    st.subheader("🧭 Navigation System & Implants")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            df,
            names="navigation_system",
            title="Navigation System Used"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            df,
            names="implants",
            title="Implant Types"
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Conversion Procedure ---
    st.subheader("🔄 Conversion Procedure")
    fig = px.bar(df["was_conversion_procedure"].value_counts().rename_axis("Conversion Procedure").reset_index(name="Count"),
                 x="Conversion Procedure", y="Count", title="Was it a Conversion Procedure?")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Please upload the Intra-Op exported CSV file to begin.")
