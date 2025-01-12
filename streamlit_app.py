import streamlit as st
import pandas as pd

# Define rows and columns for the first table
rows_dhatu = ["Rasa", "Rakta", "Mamsa", "Asthma", "Shukra"]
columns = ["Vata", "Pitta", "Kapha"]

# Define rows for the second table
rows_organs = [
    "Large Intestine", "Lungs", "Gallbladder", "Liver", "Pericardium", "Circulation",
    "Bladder", "Kidney", "Stomach", "Spleen", "Small Intestine", "Heart"
]

# Initialize session state for the tick marks
if "ticks_dhatu" not in st.session_state:
    st.session_state.ticks_dhatu = pd.DataFrame(
        False, index=rows_dhatu, columns=columns
    )


if "ticks_organs" not in st.session_state:
    st.session_state.ticks_organs = pd.DataFrame(
        False, index=rows_organs, columns=columns
    )

# Initialize session state for selections
if "dhatu_selections" not in st.session_state:
    st.session_state.dhatu_selections = []

if "organ_selections" not in st.session_state:
    st.session_state.organ_selections = []

def toggle_selection(key, df):
    """Toggle the cell selection based on Streamlit checkboxes."""
    for row in df.index:
        for col in df.columns:
            if st.session_state.get(f"{key}-{row}-{col}", False):
                df.at[row, col] = True
            else:
                df.at[row, col] = False

# Streamlit app UI

# Set the page configuration
st.set_page_config(
    page_title="Dhamani - Diagnosis",
    page_icon="📈",
    layout="wide",
)

# Sidebar Logo and Title
st.sidebar.image("Logo.png", use_column_width=True)  # Replace 'logo.png' with the path to your logo file
st.sidebar.title("AyurPragna")

# Sidebar Dropdowns
st.sidebar.subheader("User Details")
name = st.sidebar.text_input("Name:")
gender = st.sidebar.selectbox("Gender:", ["Select", "Male", "Female", "Other"])
age = st.sidebar.number_input("Age:", min_value=0, step=1)


#st.title("Dhamani - Diagnosis Solution")
# Center align the title using HTML and CSS
st.markdown(
    """
    <h1 style='text-align: center;'>
        Dhamani - Diagnosis Solution
    </h1>
    """,
    unsafe_allow_html=True
)


# Render the first table with interactive cells
st.write("### Dhatu Selection Table")
col_labels = [""] + columns  # Include empty header for row names
cols = st.columns(len(col_labels))

# Display column names
for col_index, col in enumerate(col_labels):
    with cols[col_index]:
        if col:  # Avoid empty header cell
            st.write(f"**{col}**")

# Display rows with checkboxes for the first table
for row in rows_dhatu:
    cols = st.columns(len(columns) + 1)  # Add one column for row names
    with cols[0]:
        st.write(f"**{row}**")  # Row name
    for col_index, col in enumerate(columns):
        with cols[col_index + 1]:
            st.checkbox(
                label="",
                value=st.session_state.ticks_dhatu.at[row, col],
                key=f"dhatu-{row}-{col}"
            )

# Submit button for the first table
# Submit button for the first table
if st.button("Submit Dhatu Selection"):
    toggle_selection("dhatu", st.session_state.ticks_dhatu)
    st.success("Dhatu selection has been recorded.")
    #st.write("### Dhatu Selection DataFrame")
    dhatu_selection = st.session_state.ticks_dhatu.astype(int)  # Convert boolean to 1/0
    #st.dataframe(dhatu_selection)
    
    # Process and display selected combinations
    st.session_state.dhatu_selections = [
        (row, col)
        for row in dhatu_selection.index
        for col in dhatu_selection.columns
        if dhatu_selection.at[row, col] == 1
    ]
                   
        
    

# Render the second table with interactive cells
st.write("### Organ Selection Table")
cols = st.columns(len(col_labels))

# Display column names
for col_index, col in enumerate(col_labels):
    with cols[col_index]:
        if col:  # Avoid empty header cell
            st.write(f"**{col}**")

# Display rows with checkboxes for the second table
for row in rows_organs:
    cols = st.columns(len(columns) + 1)  # Add one column for row names
    with cols[0]:
        st.write(f"**{row}**")  # Row name
    for col_index, col in enumerate(columns):
        with cols[col_index + 1]:
            st.checkbox(
                label="",
                value=st.session_state.ticks_organs.at[row, col],
                key=f"organ-{row}-{col}"
            )

# Submit button for the second table
if st.button("Submit Organ Selection"):
    toggle_selection("organ", st.session_state.ticks_organs)
    st.success("Organ selection has been recorded.")
    #st.write("### Organ Selection DataFrame")
    organ_selection = st.session_state.ticks_organs.astype(int)  # Convert boolean to 1/0
    #st.dataframe(organ_selection)
    
    # Process and display selected combinations
    st.session_state.organ_selections = [
        (row, col)
        for row in organ_selection.index
        for col in organ_selection.columns
        if organ_selection.at[row, col] == 1
    ]
    


if st.button("Start Processing"):

    #--- code to read the look-up data for diagnosis ---# 
    dhatu_data = pd.read_excel("lookup_table_dhatu_organ.xlsx", sheet_name='Dhatu')
    organ_data = pd.read_excel("lookup_table_dhatu_organ.xlsx", sheet_name='organ_right wrist')



    #--- code to filter the diagnosis based on the selections ---#

    filtered_dhatu_diagnosis = dhatu_data[dhatu_data.apply(lambda row: any(
            (row['dhatu'] == dhatu.lower() and row['vpk'] == vpk.lower()) 
            for dhatu, vpk in st.session_state.dhatu_selections
        ), axis=1)]

    probable_dhatu_diagnosis = filtered_dhatu_diagnosis['diagnosis'].tolist()

    filtered_organ_diagnosis = organ_data[organ_data.apply(lambda row: any(
            (row['organ'] == organ.lower() and row['vpk'] == vpk.lower()) 
            for organ, vpk in st.session_state.organ_selections
        ), axis=1)]

    probable_organ_diagnosis = filtered_organ_diagnosis['conditions'].tolist()



    #----- Display ----# 
    st.write("### Probable Diagnosis:")
    col1, col2 = st.columns(2)

    with col1:
        st.write("#### Dhatu-based Diagnoses")
        if probable_dhatu_diagnosis:
            for i, diagnosis in enumerate(probable_dhatu_diagnosis, 1):
                st.write(f"{i}. {diagnosis}")
        else:
            st.write("No dhatu-based diagnoses found.")

    # Display Organ diagnoses in the right column
    with col2:
        st.write("#### Organ-based Diagnoses")
        if probable_organ_diagnosis:
            for i, conditions in enumerate(probable_organ_diagnosis, 1):
                st.write(f"{i}. {conditions}")
        else:
            st.write("No organ-based diagnoses found.")

