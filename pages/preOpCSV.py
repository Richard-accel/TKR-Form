import streamlit as st
import pandas as pd
import requests
import base64

# --- CONFIG ---
FHIR_BASE_URL = st.secrets["FHIR_BASE_URL"]
FHIR_BEARER_TOKEN = st.secrets["FHIR_BEARER_TOKEN"]

headers = {
    "Authorization": f"Bearer {FHIR_BEARER_TOKEN}"
}

# --- HELPERS ---

def get_questionnaire_responses():
    params = {
        "questionnaire": "https://novoheal.com/TKR_PreOp_Assessment"
    }
    response = requests.get(f"{FHIR_BASE_URL}/QuestionnaireResponse", headers=headers, params=params)
    response.raise_for_status()
    
    return response.json().get('entry', [])

def extract_by_linkid(items, linkid):
    if not isinstance(items, list):
        return None

    for item in items:
        if item.get("linkId") == linkid and "answer" in item:
            answers = item["answer"]
            values = []

            for answer in answers:
                val = answer.get("value") or {}

                # Handle valueCoding (multi-answer like diagnosis)
                if isinstance(val, dict):
                    if "Coding" in val:
                        coding = val["Coding"]
                        display = coding.get("display") or coding.get("code")
                        values.append(display.strip() if display else "")
                    else:
                        # fallback for other types
                        for key in ["string", "boolean", "integer", "date"]:
                            if key in val:
                                values.append(str(val[key]))
                else:
                    values.append(str(val))

            return ", ".join(filter(None, values)) if values else None

        # Recursively search nested items
        if "item" in item:
            nested = extract_by_linkid(item["item"], linkid)
            if nested is not None:
                return nested

    return None


def list_all_linkids(items, level=0):
    if not isinstance(items, list):
        return
    for item in items:
        st.write("  " * level + f"linkId: {item.get('linkId')}")
        if "item" in item:
            list_all_linkids(item["item"], level + 1)


def extract_signature_data(items):
    for item in items:
        if item.get("linkId") == "Wzw_ds6Q" and "answer" in item:
            value = item["answer"][0].get("value", {})
            attachment = value.get("Attachment")
            if attachment and "data" in attachment:
                return "data:image/png;base64," + attachment["data"]

        # Recursively check nested items
        if "item" in item:
            nested = extract_signature_data(item["item"])
            if nested:
                return nested
    return None


# Usage:
# list_all_linkids(response["resource"]["item"])


def parse_response(response):
    item = response["resource"]["item"]
    patient_id = response["resource"]["subject"]["id"]
    form_id = response["resource"]["id"]

    return {
        "form_id": form_id,
        "patient_id": patient_id,
        "mrn": extract_by_linkid(item, "patient-info-mrn"),
        "age": extract_by_linkid(item, "patient-info-age"),
        "gender": extract_by_linkid(item, "patient-info-gender"),
        "race": extract_by_linkid(item, "patient-info-race"),
        "nationality": extract_by_linkid(item, "patient-info-nationality"),
        "caregiver_present": extract_by_linkid(item, "patient-info-caregiver"),
        "hospital": extract_by_linkid(item, "hospital-info-hospital"),
        "consultant": extract_by_linkid(item, "hospital-info-consultant"),
        "surgeon": extract_by_linkid(item, "hospital-info-surgeon"),
        "assistant_present": extract_by_linkid(item, "hospital-info-assistant"),
        "diagnosis": extract_by_linkid(item, "diagnosis-info-diagnosis"),
        "urgency": extract_by_linkid(item, "urgency-and-medical-history-urgency"),
        "previous_knee_surgery": extract_by_linkid(item, "medical-history-previous-knee-surgery"),
        "vte_cardiovascular_risk": extract_by_linkid(item, "medical-history-vte-risk"),
        "chronic_lung_disease": extract_by_linkid(item, "medical-history-chronic-lung-disease"),
        "diabetes_on_insulin": extract_by_linkid(item, "medical-history-diabetes-insulin"),
        "admission_date": extract_by_linkid(item, "admission-date"),
        "surgery_date": extract_by_linkid(item, "surgery-date"),
        "surgery_access": extract_by_linkid(item, "surgical-access"),
        "surgery_type": extract_by_linkid(item, "surgery-operation-type"),
        "patient_education_received": extract_by_linkid(item, "patient-education"),
        "caregiver_education": extract_by_linkid(item, "caregiver-education"),
        "qol_comleteted": extract_by_linkid(item, "patient-education-health-status-qol-completed"),
        "pain_vas": extract_by_linkid(item, "patient-education-health-status-pain-vas"),
        "current_infection": extract_by_linkid(item, "patient-education-health-status-current-infections"),
        "recent_infection": extract_by_linkid(item, "patient-education-health-status-recent-infections"),
        "smoke": extract_by_linkid(item, "risk-lifestyle-smoking"),
        "alcohol": extract_by_linkid(item, "risk-lifestyle-alcohol"),
        "comorbidities": extract_by_linkid(item, "risk-lifestyle-comorbidities"),
        "blood_thinners": extract_by_linkid(item, "medications-blood-thinners"),
        "beta_blockers": extract_by_linkid(item, "medications-beta-blockers"),
        "statins": extract_by_linkid(item, "medications-statins"),
        "arbs": extract_by_linkid(item, "medications-arbs"),
        "ace_inhibitors": extract_by_linkid(item, "medications-ace-inhibitors"),
        "diuretics": extract_by_linkid(item, "medications-diuretics"),
        "charnley": extract_by_linkid(item, "functional-clinical-assessment-charnley"),
        "anatomic_alignment": extract_by_linkid(item, "functional-clinical-assessment-alignment"),
        "ml_extension_rating": extract_by_linkid(item, "ml-instability-extension-rating"),
        "ml_flexion_rating": extract_by_linkid(item, "ml-instability-flexion-rating"),
        "ap_extension_rating": extract_by_linkid(item, "ap-instability-extension-rating"),
        "ap_flexion_rating": extract_by_linkid(item, "ap-instability-flexion-rating"),
        "extension_range": extract_by_linkid(item, "rom-extension-range"),
        "flexion_range": extract_by_linkid(item, "rom-flexion-range"),
        "flexion_contracture_deductions": extract_by_linkid(item, "functional-clinical-assessment-flexion-deduction"),
        "extensor_lag_deductions": extract_by_linkid(item, "functional-clinical-assessment-extensor-deduction"),
        "morse_fall_risk_scale": extract_by_linkid(item, "functional-clinical-assessment-morse-fall"),
         "signature_base64": extract_signature_data(item)
    }

# --- STREAMLIT APP ---

st.title("Export TKR Pre-Op Assessment to CSV")

if st.button("Load data"):
    with st.spinner("Fetching data..."):
        try:
            responses = get_questionnaire_responses()
            parsed = [parse_response(entry) for entry in responses]
            df = pd.DataFrame(parsed)

            # Replace any problematic characters
            df = df.applymap(lambda x: x.replace("–", "-").replace("—", "-") if isinstance(x, str) else x)

            csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

            st.success("Data loaded successfully!")

            st.download_button(
                label="📥 Download CSV file",
                data=csv_bytes,
                file_name="TKR_PreOp_Assessments.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")

