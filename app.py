import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# Create sample college dataset
# -----------------------------
data = {
    "College": ["IIT Delhi", "NIT Jaipur", "BITS Pilani", "SRM University", "Amity University"],
    "General_Cutoff": [95, 85, 90, 70, 60],
    "OBC_Cutoff": [90, 80, 85, 65, 55],
    "SC_Cutoff": [75, 65, 70, 50, 45],
    "ST_Cutoff": [70, 60, 65, 45, 40],
    "Management_Cutoff": [60, 55, 60, 40, 35]
}

df = pd.DataFrame(data)

# -----------------------------
# Streamlit App UI
# -----------------------------
st.set_page_config(page_title="🎓 College Allotment App", layout="centered")

st.title("🎓 College Allotment System")
st.write("Get your allotted college based on your score and category!")

# -----------------------------
# Input from user
# -----------------------------
score = st.number_input("Enter your Exam Score (out of 100):", min_value=0, max_value=100)
category = st.selectbox("Select your Category:", ["General", "OBC", "SC", "ST", "Management"])

# -----------------------------
# Processing Logic
# -----------------------------
if st.button("Find My College"):
    cutoff_col = f"{category}_Cutoff"
    
    # Filter colleges where score >= cutoff
    eligible_colleges = df[df[cutoff_col] <= score]
    
    if not eligible_colleges.empty:
        st.success("🎯 Based on your score, you are eligible for the following colleges:")
        st.dataframe(eligible_colleges[["College", cutoff_col]].rename(columns={cutoff_col: "Your Category Cutoff"}))
        
        # Best college = highest cutoff <= score
        best_college = eligible_colleges.sort_values(by=cutoff_col, ascending=False).iloc[0]["College"]
        st.subheader(f"🏆 You are allotted: **{best_college}**")
    else:
        st.error("❌ Sorry, your score is below all college cutoffs. Try again next year!")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Developed with ❤️ using Streamlit and Pandas.")
