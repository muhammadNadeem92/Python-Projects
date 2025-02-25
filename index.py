
import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Page setup
st.set_page_config(page_title="📀 Data Sweeper", layout="wide")

# Custom CSS for style
st.markdown("""
    <style>
        .stApp {
            background-color: #121212;
            color: white;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📀 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# Initialize session state for dataframes
if 'file_data' not in st.session_state:
    st.session_state.file_data = {}

# File Uploader
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", 
                                 type=["csv", "xlsx"],
                                 accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_name = file.name
        file_ext = os.path.splitext(file_name)[-1].lower()
        
        # Initialize dataframe in session state if not exists
        if file_name not in st.session_state.file_data:
            try:
                if file_ext == ".csv":
                    df = pd.read_csv(file)
                elif file_ext == ".xlsx":
                    df = pd.read_excel(file, engine='openpyxl')
                st.session_state.file_data[file_name] = df
            except Exception as e:
                st.error(f"Error reading {file_name}: {str(e)}")
                continue
        
        df = st.session_state.file_data[file_name]
        
        # Display file info
        st.subheader(f"File: {file_name}")
        st.write(f"**File Size:** {file.getbuffer().nbytes / 1024:.2f} KB")
        
        # Show dataframe preview
        st.write("🔍 Preview the Head of the Dataframe")
        st.dataframe(df,height=200)

        # Data cleaning options
        st.subheader("📀 Data Cleaning Options")
        clean_key = f"clean_{file_name}"
        if st.checkbox(f"Clean Data for {file_name}", key=clean_key):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Remove Duplicates from {file_name}"):
                    df = df.drop_duplicates()
                    st.session_state.file_data[file_name] = df
                    st.success("✅ Duplicates Removed!")
            
            with col2:
                if st.button(f"Fill Missing Values for {file_name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.session_state.file_data[file_name] = df
                    st.success("✅ Missing Values Filled!")

        # Column selection
        st.subheader("🔄 Select Columns to Keep")
        columns = st.multiselect(f"Choose columns for {file_name}", 
                                df.columns,
                                default=list(df.columns),
                                key=f"cols_{file_name}")
        df = df[columns]
        st.session_state.file_data[file_name] = df

        # Data visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show visualization for {file_name}", key=f"viz_{file_name}"):
            if df.select_dtypes(include='number').shape[1] >= 2:
                st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])
            else:
                st.warning("Need at least 2 numeric columns for visualization")

        # File conversion
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file_name} to:",
                                 ["CSV", "Excel"],
                                 key=f"conv_{file_name}")
        
        if st.button(f"Convert {file_name}", key=f"btn_{file_name}"):
            buffer = BytesIO()
            try:
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name_new = file_name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                else:
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    file_name_new = file_name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                buffer.seek(0)
                st.download_button(
                    label=f"📥 Download {file_name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name_new,
                    mime=mime_type,
                    key=f"dl_{file_name}"
                )
            except Exception as e:
                st.error(f"Conversion failed: {str(e)}")

    st.success("All files processed! 🎉")