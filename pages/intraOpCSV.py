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
        "questionnaire": "https://novoheal.com/TKR_IntraOp_Assessment"
    }
    response = requests.get(f"{FHIR_BASE_URL}/QuestionnaireResponse", headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('entry', [])

def extract_value_from_answer(answer):
    """Extracts raw value from the answer dict."""
    if "value" in answer:
        value = answer["value"]
        if isinstance(value, dict):
            # Check for types inside `value`
            if "boolean" in value:
                return value["boolean"]
            elif "integer" in value:
                return value["integer"]
            elif "string" in value:
                return value["string"]
            elif "date" in value:
                return value["date"]
            elif "Coding" in value:
                return value["Coding"].get("display") or value["Coding"].get("code")
            elif "Reference" in value:
                return value["Reference"].get("id") or value["Reference"].get("reference")
        else:
            return value
    return None

def extract_by_linkid(items, target_linkid):
    if not isinstance(items, list):
        return None

    for item in items:
        if item.get("linkId") == target_linkid and "answer" in item:
            return extract_value_from_answer(item["answer"][0])

        # Recurse into nested groups
        if "item" in item:
            nested = extract_by_linkid(item["item"], target_linkid)
            if nested is not None:
                return nested

    return None

def parse_response(response):
    r = response["resource"]
    items = r.get("item", [])

    return {
        "form_id": r.get("id"),
        "patient_id": r.get("subject", {}).get("id"),
        "blood_loss": extract_by_linkid(items, "blood-loss"),
        "surgical_complications": extract_by_linkid(items, "surgical-complications"),
        "anaesthetic_complications": extract_by_linkid(items, "anaesthetic-complications"),
        "prophylactic_antibiotics": extract_by_linkid(items, "prophylactic-antibiotics"),
        "pain_management": extract_by_linkid(items, "pain-management"),
        "anticoagulants": extract_by_linkid(items, "anticoagulants"),
        "traditional_surgery": extract_by_linkid(items, "traditional-open-surgery"),
        "minimally_invasive": extract_by_linkid(items, "minimally-invasive"),
        "proper_alignment_prosthesis": extract_by_linkid(items, "alignment"),
        "navigation_system": extract_by_linkid(items, "navigation-system"),
        "implants": extract_by_linkid(items, "implants"),
        "was_conversion_procedure": extract_by_linkid(items, "conversion"),
    }

# --- STREAMLIT APP ---
st.title("Export TKR Intra-Op Assessment to CSV")

if st.button("Load data"):
    with st.spinner("Fetching data..."):
        try:
            responses = get_questionnaire_responses()
            parsed = [parse_response(entry) for entry in responses]
            df = pd.DataFrame(parsed)

            csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

            st.success("Data loaded successfully!")

            st.download_button(
                label="📥 Download TKR Intra-Op CSV",
                data=csv_bytes,
                file_name="TKR_IntraOp_Assessments.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
