import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title="TKR Pre-Op Dashboard", layout="wide")

st.title("🦵 TKR Pre-Op Assessment Dashboard")

# --- Load Data ---
uploaded_file = st.file_uploader("Upload exported CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="utf-8-sig")

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    consultants = st.sidebar.multiselect("Select Consultant(s)", options=df["consultant"].dropna().unique())
    surgeons = st.sidebar.multiselect("Select Surgeon(s)", options=df["surgeon"].dropna().unique())

    filtered_df = df.copy()
    if consultants:
        filtered_df = filtered_df[filtered_df["consultant"].isin(consultants)]
    if surgeons:
        filtered_df = filtered_df[filtered_df["surgeon"].isin(surgeons)]

    # --- Dashboard Sections ---
    st.subheader("👤 Patient Demographics")
    col1, col2, col3 = st.columns(3)

    with col1:
        fig = px.pie(
            filtered_df,
            names="gender",
            title="Gender Distribution",
            color="gender",
            color_discrete_map={
                "female": "#F38581",
                "male": "#61C4C1"
            }
        )
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        bins = [0, 40, 50, 60, 70, 100]
        labels = ['<40', '40-50', '50-60', '60-70', '70+']
        filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=bins, labels=labels, right=False)
        fig = px.bar(filtered_df['age_group'].value_counts().sort_index(), title="Age Group Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        fig = px.pie(filtered_df, names="nationality", title="Nationality")
        st.plotly_chart(fig, use_container_width=True)

    # --- Clinical Risks ---
    st.subheader("⚠️ Pre-Operative Risk Factors")
    risk_cols = ["vte_cardiovascular_risk", "chronic_lung_disease", "diabetes_on_insulin"]

    # Normalize values to "Yes", "No", or "Unknown"
    def normalize_bool(val):
        if pd.isna(val):
            return "Unknown"
        val = str(val).strip().lower()
        if val in ["yes", "true", "1"]:
            return "Yes"
        elif val in ["no", "false", "0"]:
            return "No"
        return "Unknown"

    risk_df = filtered_df[risk_cols].applymap(normalize_bool).apply(pd.Series.value_counts).T
    # Ensure consistent column order
    for col in ["Yes", "No"]:
        if col not in risk_df.columns:
            risk_df[col] = 0
    risk_df = risk_df[["Yes", "No"]]
    st.bar_chart(risk_df["Yes"])


    # --- Surgery Details ---
    st.subheader("🛠️ Surgical Details")
    col4, col5 = st.columns(2)

    with col4:
        fig = px.bar(filtered_df["surgery_access"].value_counts(), title="Surgical Access Type")
        st.plotly_chart(fig, use_container_width=True)

    with col5:
        fig = px.bar(filtered_df["surgery_type"].value_counts(), title="Operation Type")
        st.plotly_chart(fig, use_container_width=True)

    # --- Education & Preparation ---
    st.subheader("📚 Education & Pre-Op Readiness")
    prep_cols = ["patient_education_received", "caregiver_education", "qol_comleteted"]
    st.dataframe(filtered_df[prep_cols].apply(pd.Series.value_counts))

    # --- Medications ---
    st.subheader("💊 Medication Summary")
    med_cols = ["blood_thinners", "beta_blockers", "statins", "arbs", "ace_inhibitors", "diuretics"]
    meds_df = filtered_df[med_cols].applymap(normalize_bool).apply(pd.Series.value_counts).T
    for col in ["Yes", "No"]:
        if col not in meds_df.columns:
            meds_df[col] = 0
    meds_df = meds_df[["Yes", "No"]]
    st.bar_chart(meds_df["Yes"])


    # --- Functional Assessment ---
    st.subheader("🦿 Functional & Clinical Assessment")
    col6, col7 = st.columns(2)

    with col6:
        fig = px.histogram(
            filtered_df,
            x="extension_range",
            nbins=21,  # one bin per integer from -10 to 10
            title="Extension Range Distribution"
        )
        fig.update_traces(marker_line_color="black", marker_line_width=1)
        fig.update_xaxes(range=[-10, 10])
        st.plotly_chart(fig, use_container_width=True)

    with col7:
        fig = px.histogram(
            filtered_df,
            x="flexion_range",
            nbins=16,  # adjust based on your data; e.g., bins of 10° from 0–160
            title="Flexion Range Distribution"
        )
        fig.update_traces(marker_line_color="black", marker_line_width=1)
        fig.update_xaxes(range=[0, 160])  # or 0–150 depending on your form
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📉 Instability Ratings")
    instability_cols = [
        "ml_extension_rating", "ml_flexion_rating", 
        "ap_extension_rating", "ap_flexion_rating"
    ]
    for col in instability_cols:
        fig = px.bar(filtered_df[col].value_counts(), title=col.replace("_", " ").title())
        st.plotly_chart(fig, use_container_width=True)


else:
    st.info("Please upload a TKR Pre-Op CSV file to begin.")
