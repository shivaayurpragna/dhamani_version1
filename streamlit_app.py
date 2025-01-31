import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# Define rows and columns for the first table
rows_dhatu = ["Rasa", "Rakta", "Mamsa", "Medas", "Asthi", "Majja", "Shukra", "Artava"]
columns = ["Vata", "Pitta", "Kapha"]

# Define rows for the second table
rows_organs = [
    "Large Intestine", "Lungs", "Gallbladder", "Liver", "Pericardium", "Circulation",
    "Bladder", "Kidney", "Stomach", "Spleen", "Small Intestine", "Heart"
]

# Initialize session state **outside of button conditions**
if "ticks_dhatu" not in st.session_state:
    st.session_state.ticks_dhatu = pd.DataFrame(False, index=rows_dhatu, columns=columns)

if "ticks_organs" not in st.session_state:
    st.session_state.ticks_organs = pd.DataFrame(False, index=rows_organs, columns=columns)

if "dhatu_selections" not in st.session_state:
    st.session_state.dhatu_selections = []

if "organ_selections" not in st.session_state:
    st.session_state.organ_selections = []

# Function to toggle selections
def toggle_selection(key, df):
    for row in df.index:
        for col in df.columns:
            df.at[row, col] = st.session_state.get(f"{key}-{row}-{col}", False)

# Set the page configuration
st.set_page_config(page_title="Dhamani - Diagnosis", page_icon="📈", layout="wide")

# Sidebar Logo and Title
st.sidebar.image("Logo.png", use_column_width=True)
st.sidebar.title("AyurPragna")

customer_type = st.radio("Select Customer Type:", ("New Customer", "Repeat Customer"))

if customer_type == "New Customer":
    st.subheader("New Customer Registration")
    name = st.text_input("Name")
    gender = st.radio("Gender", ("Male", "Female", "Other"))
    dob = st.date_input("Date of Birth", value=datetime(2000, 1, 1))

    if st.button("Submit"):
        try:
            read_url = "http://98.70.52.225:8000/read"
            response = requests.get(read_url, params={"collection": "user_data"})
            collection_data = response.json()
            user_ids = [doc["user_id"] for doc in collection_data if "user_id" in doc]
            max_user_id = max(user_ids, default=0)
            user_id = max_user_id + 1

            post_url = "http://98.70.52.225:8000/insert"
            json_data = {"collection": "user_data", "data": [{"user_id": user_id, "name": name, "gender": gender, "dob": dob.isoformat()}]}
            requests.post(post_url, json=json_data)

            st.success(f"Registration Successful! Welcome, {name}.")
            st.session_state.user_id = user_id
        except Exception as e:
            st.error(f"Error: {e}")

elif customer_type == "Repeat Customer":
    st.subheader("Repeat Customer Lookup")
    search_name = st.text_input("Enter your name:")

    if st.button("Search"):
        read_url = "http://98.70.52.225:8000/read"
        query = {"name": {"$regex": search_name, "$options": "i"}}
        get_data = requests.get(read_url, params={"collection": "user_data", "query": query})

        if not get_data.json():
            st.error("No user found with the given name.")
        else:
            user_search = pd.DataFrame(get_data.json())
            selected_user = st.selectbox("Select a User", options=user_search.to_dict("records"), format_func=lambda x: x["name"])

            if selected_user:
                st.session_state.user_id = selected_user["user_id"]

# --- Start Diagnosis ---
if st.button("Start Diagnosis") or "diagnosis_started" in st.session_state:
    st.session_state.diagnosis_started = True

if "diagnosis_started" in st.session_state:
    st.write("### Dhatu Selection Table")
    col_labels = [""] + columns
    cols = st.columns(len(col_labels))

    for col_index, col in enumerate(col_labels):
        with cols[col_index]:
            if col:
                st.write(f"**{col}**")

    for row in rows_dhatu:
        cols = st.columns(len(columns) + 1)
        with cols[0]:
            st.write(f"**{row}**")
        for col_index, col in enumerate(columns):
            with cols[col_index + 1]:
                st.session_state.ticks_dhatu.at[row, col] = st.checkbox(
                    label=" ",  # Use a space instead of an empty string to avoid accessibility warnings
                    value=st.session_state.ticks_dhatu.at[row, col],
                    key=f"dhatu-{row}-{col}"
                )

    if st.button("Submit Dhatu Selection"):
        toggle_selection("dhatu", st.session_state.ticks_dhatu)
        st.success("Dhatu selection has been recorded.")
        st.session_state.dhatu_selections = [
            (row, col)
            for row in st.session_state.ticks_dhatu.index
            for col in st.session_state.ticks_dhatu.columns
            if st.session_state.ticks_dhatu.at[row, col]
        ]

    st.write("### Organ Selection Table")
    cols = st.columns(len(col_labels))

    for col_index, col in enumerate(col_labels):
        with cols[col_index]:
            if col:
                st.write(f"**{col}**")

    for row in rows_organs:
        cols = st.columns(len(columns) + 1)
        with cols[0]:
            st.write(f"**{row}**")
        for col_index, col in enumerate(columns):
            with cols[col_index + 1]:
                st.session_state.ticks_organs.at[row, col] = st.checkbox(
                label=" ",  # Use a space instead of an empty label to prevent accessibility warnings
                value=st.session_state.ticks_organs.at[row, col],
                key=f"organ-{row}-{col}"
            )


    if st.button("Submit Organ Selection"):
        toggle_selection("organ", st.session_state.ticks_organs)
        st.success("Organ selection has been recorded.")
        st.session_state.organ_selections = [
            (row, col)
            for row in st.session_state.ticks_organs.index
            for col in st.session_state.ticks_organs.columns
            if st.session_state.ticks_organs.at[row, col]
        ]

    if st.button("Start Processing"):
        dhatu_data = pd.read_excel("lookup_table_dhatu_organ.xlsx", sheet_name="Dhatu")
        organ_data = pd.read_excel("lookup_table_dhatu_organ.xlsx", sheet_name="organ_right wrist")

        filtered_dhatu_diagnosis = dhatu_data[
            dhatu_data.apply(lambda row: any(
                (row["dhatu"] == dhatu.lower() and row["vpk"] == vpk.lower()) 
                for dhatu, vpk in st.session_state.dhatu_selections
            ), axis=1)
        ]

        filtered_organ_diagnosis = organ_data[
            organ_data.apply(lambda row: any(
                (row["organ"] == organ.lower() and row["vpk"] == vpk.lower()) 
                for organ, vpk in st.session_state.organ_selections
            ), axis=1)
        ]

        st.write("### 🏥 Probable Diagnosis:")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔬 Dhatu-based Diagnoses")
            if not filtered_dhatu_diagnosis.empty:  
                for condition in filtered_dhatu_diagnosis["diagnosis"]:
                    st.markdown(f"- **{condition}**")  # Bullet points for clarity
            else:
                st.info("No probable diagnosis found for the selected Dhatu.")

        with col2:
            st.subheader("🫀 Organ-based Diagnoses")
            if not filtered_organ_diagnosis.empty:
                for condition in filtered_organ_diagnosis["conditions"]:
                    st.markdown(f"- **{condition}**")  # Bullet points for clarity
            else:
                st.info("No probable diagnosis found for the selected Organ.")

