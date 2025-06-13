import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="TKR Post-Op Dashboard", layout="wide")

st.title("🦿 TKR Post-Op Assessment Dashboard")

# Upload CSV
uploaded_file = st.file_uploader("Upload Post-Op CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Convert all TRUE/FALSE to boolean
    df.replace({"TRUE": True, "FALSE": False, "": None}, inplace=True)

    # -----------------------
    st.header("📊 Score Distributions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**🩺 Pain VAS (0–10)**")
        vas_counts = df['pain_vas'].dropna().astype(int).value_counts().sort_index()
        vas_range = list(range(0, 10))
        vas_counts = vas_counts.reindex(vas_range, fill_value=0)
        fig_vas = px.bar(
            x=vas_counts.values,
            y=vas_counts.index,
            orientation='h',
            labels={"x": "Count", "y": "VAS Score"},
            height=300
        )
        st.plotly_chart(fig_vas, use_container_width=True)

    with col2:
        st.markdown("**😊 Patient Satisfaction (1–5)**")
        psat_counts = df['patient_satisfaction'].dropna().astype(int).value_counts().sort_index()
        psat_range = list(range(1, 5))
        psat_counts = psat_counts.reindex(psat_range, fill_value=0)
        fig_psat = px.bar(
            x=psat_counts.values,
            y=psat_counts.index,
            orientation='h',
            labels={"x": "Count", "y": "Patient Sat."},
            height=300
        )
        st.plotly_chart(fig_psat, use_container_width=True)

    with col3:
        st.markdown("**🧑‍⚕️ Caregiver Satisfaction (1–5)**")
        csat_counts = df['caregiver_satisfaction'].dropna().astype(int).value_counts().sort_index()
        csat_range = list(range(1, 5))
        csat_counts = csat_counts.reindex(csat_range, fill_value=0)
        fig_csat = px.bar(
            x=csat_counts.values,
            y=csat_counts.index,
            orientation='h',
            labels={"x": "Count", "y": "Caregiver Sat."},
            height=300
        )
        st.plotly_chart(fig_csat, use_container_width=True)

    with col4:
        st.markdown("**🏥 Length of Stay**")
        los_data = df['length_of_stay'].dropna()
        fig_los = px.histogram(
            los_data,
            nbins=len(los_data.unique()),
            labels={"value": "Days", "count": "Patients"},
            height=300
        )
        # Add black outline to bars
        fig_los.update_traces(
            marker_line_color='black',
            marker_line_width=1.5
        )
        st.plotly_chart(fig_los, use_container_width=True)

    # -----------------------
    st.subheader("🧬 Complications")
    complications = [
        'surgical_site_infection', 'blood_clots', 'nerve_damage', 'knee_stiffness',
        'implant_problems', 'dislocation', 'reopen'
    ]
    comp_counts = df[complications].sum().sort_values(ascending=False)
    fig = px.bar(comp_counts, x=comp_counts.index.str.replace('_', ' ').str.title(), y=comp_counts.values,
                 title="Complications Count", labels={"x": "Complication", "y": "Count"})
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------
    st.subheader("💊 Medications Administered")
    meds = ['pain_management', 'antibiotics', 'anticoagulants', 'antiemetics', 'analgesics']
    med_counts = df[meds].sum().sort_values(ascending=False)
    fig2 = px.pie(values=med_counts.values, names=med_counts.index.str.replace('_', ' ').str.title(),
                  title="Medication Types Given")
    st.plotly_chart(fig2, use_container_width=True)

    # -----------------------
    st.subheader("📘 Education & QoL")
    col5, col6 = st.columns(2)

    with col5:
        edu_fields = ['patient_education', 'caregiver_education']
        edu_counts = df[edu_fields].sum()
        fig3 = px.pie(values=edu_counts.values, names=edu_counts.index.str.replace('_', ' ').str.title(),
                      title="Education Provided")
        st.plotly_chart(fig3, use_container_width=True)

    with col6:
        qol_fields = ['qol_completed', 'qol_improved']
        qol_counts = df[qol_fields].sum()
        fig4 = px.bar(x=qol_counts.index.str.replace('_', ' ').str.title(), y=qol_counts.values,
                      title="QoL Questionnaire Responses", labels={"x": "QoL Field", "y": "Count"})
        st.plotly_chart(fig4, use_container_width=True)

    # -----------------------
    st.subheader("📈 Recovery Metrics")
    recovery_metrics = [
        'early_mobilization', 'readmission_30_days', 'death_within_30_days', 'antibiotic_discontinuation'
    ]
    recovery_counts = df[recovery_metrics].sum()
    fig5 = px.bar(x=recovery_counts.index.str.replace('_', ' ').str.title(), y=recovery_counts.values,
                  title="Recovery Indicators", labels={"x": "Metric", "y": "Count"})
    st.plotly_chart(fig5, use_container_width=True)


else:
    st.info("📂 Please upload a Post-Op CSV file to continue.")
