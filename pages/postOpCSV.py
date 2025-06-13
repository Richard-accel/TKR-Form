import streamlit as st
import pandas as pd
import requests

# --- CONFIG ---
FHIR_BASE_URL = st.secrets["FHIR_BASE_URL"]
FHIR_BEARER_TOKEN = st.secrets["FHIR_BEARER_TOKEN"]

headers = {
    "Authorization": f"Bearer {FHIR_BEARER_TOKEN}"
}

# --- HELPERS ---

def get_questionnaire_responses():
    params = {
        "questionnaire": "https://novoheal.com/TKR_PostOp_Assessment"
    }
    response = requests.get(f"{FHIR_BASE_URL}/QuestionnaireResponse", headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('entry', [])

def extract_by_linkid(items, linkid):
    if not isinstance(items, list):
        return None

    for item in items:
        if item.get("linkId") == linkid and "answer" in item:
            answer = item["answer"][0]
            for value_type in ["integer", "boolean", "string", "date"]:
                if value_type in answer.get("value", {}):
                    return answer["value"][value_type]
            if "value" in answer and "Coding" in answer["value"]:
                return answer["value"]["Coding"].get("display") or answer["value"]["Coding"].get("code")
            if "value" in answer and "Reference" in answer["value"]:
                return answer["value"]["Reference"].get("id") or answer["value"]["Reference"].get("reference")

        if "item" in item:
            nested = extract_by_linkid(item["item"], linkid)
            if nested is not None:
                return nested

    return None

def parse_response(response):
    r = response["resource"]
    items = r.get("item", [])

    return {
        "form_id": r.get("id"),
        "patient_id": r.get("subject", {}).get("id"),
        "surgical_site_infection": extract_by_linkid(items, "surgical-site-infection"),
        "blood_clots": extract_by_linkid(items, "blood-clots"),
        "nerve_damage": extract_by_linkid(items, "nerve-damage"),
        "knee_stiffness": extract_by_linkid(items, "knee-stiffness"),
        "implant_problems": extract_by_linkid(items, "implant-problems"),
        "dislocation": extract_by_linkid(items, "dislocation"),
        "reopen": extract_by_linkid(items, "reoperation"),
        "pain_management": extract_by_linkid(items, "pain-management"),
        "antibiotics": extract_by_linkid(items, "antibiotics"),
        "anticoagulants": extract_by_linkid(items, "anticoagulants"),
        "antiemetics": extract_by_linkid(items, "antiemetics"),
        "analgesics": extract_by_linkid(items, "analgesics"),
        "patient_education": extract_by_linkid(items, "patient-education"),
        "caregiver_education": extract_by_linkid(items, "caregiver-education"),
        "qol_completed": extract_by_linkid(items, "qol-questionnaire-completed"),
        "qol_improved": extract_by_linkid(items, "qol-questionnaire-improved"),
        "pain_vas": extract_by_linkid(items, "pain-vas"),
        "wound_healing": extract_by_linkid(items, "wound-healing"),
        "support_measure": extract_by_linkid(items, "support-measure"),
        "patient_satisfaction": extract_by_linkid(items, "patient-satisfaction"),
        "caregiver_satisfaction": extract_by_linkid(items, "caregiver-satisfaction"),
        "length_of_stay": extract_by_linkid(items, "length-of-stay"),
        "day_stepdown_cicu": extract_by_linkid(items, "day-stepdown-cicu"),
        "readmission_30_days": extract_by_linkid(items, "readmission-30-days"),
        "rehabilitation": extract_by_linkid(items, "rehab-progress"),
        "early_mobilization": extract_by_linkid(items, "early-mobilization"),
        "death_within_30_days": extract_by_linkid(items, "death-within-30-days"),
        "antibiotic_discontinuation": extract_by_linkid(items, "antibiotic-discontinuation"),
    }

# --- STREAMLIT APP ---

st.title("Export TKR Post-Op Assessment to CSV")

if st.button("Load data"):
    with st.spinner("Fetching data..."):
        try:
            responses = get_questionnaire_responses()
            parsed = [parse_response(entry) for entry in responses]
            df = pd.DataFrame(parsed)

            # Optional data cleaning
            df = df.applymap(lambda x: x.replace("–", "-").replace("—", "-") if isinstance(x, str) else x)

            csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

            st.success("✅ Data loaded successfully!")

            st.download_button(
                label="📥 Download TKR Post-Op CSV",
                data=csv_bytes,
                file_name="TKR_PostOp_Assessments.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
