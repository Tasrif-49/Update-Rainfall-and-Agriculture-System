
# ABOUT.PY — QUICK DEVELOPER INDEX


# [01] IMPORTS
#      → Streamlit
#
# [02] SHOW ABOUT FUNCTION
#      → Main About page controller
#
# [03] ABOUT PAGE TITLE
#      → "About System"
#
# [04] ABOUT PAGE CONTENT
#      → Rainfall Prediction System
#      → Smart Agriculture System
#      → Machine Learning
#      → Developed By
#
#      [04-A] RAINFALL PREDICTION SYSTEM
#             → Model
#             → Prediction target
#             → Features
#
#      [04-B] SMART AGRICULTURE SYSTEM
#             → Crop water requirement
#             → Land area
#             → Predicted rainfall
#             → Existing water
#             → Soil type
#             → Growth stage
#             → ET0
#             → Irrigation efficiency
#
#      [04-C] MACHINE LEARNING
#             → CatBoost Regression explanation
#
#      [04-D] DEVELOPED BY
#             → Developer/team names
#
# QUICK CHANGE GUIDE

#
# About page title
#      → [03]
#
# Rainfall model information
#      → [04-A]
#
# Agriculture information
#      → [04-B]
#
# Machine Learning information
#      → [04-C]
#
# Developer names
#      → [04-D]
#
# IMPORTANT:
# Developer comments MUST stay outside the st.markdown()
# content string.
#
# Never put [04-A], [04-B], [04-C], [04-D] or other
# developer comments inside the Markdown content.



# [01] IMPORTS


import streamlit as st


# [02] MAIN ABOUT PAGE FUNCTION

#
# Function:
#     show_about()
#
# This function displays the complete About page.

def show_about():


    # [03] ABOUT PAGE TITLE


    st.title(
        "ℹ️ About System"
    )


    # [04] ABOUT PAGE CONTENT

    #
    # IMPORTANT:
    # Keep this Markdown content clean.
    #
    # DO NOT put developer index comments inside this string.


    st.markdown(

        """

        ### 🌧️ Bangladesh Rainfall Prediction System

        **Model:** CatBoost Regression

        **Prediction Target:** Daily Rainfall (mm)

        **Features:**
        Weather, Calendar, Lag, Rolling & Station Features


        ---


        ### 🌱 Smart Agriculture System

        এই অংশে ব্যবহারকারী জানতে পারবেন:

        - 🌾 কোন ফসল কত পানি চায়

        - 📐 জমির পরিমাণ অনুযায়ী মোট পানি

        - 🌧️ predicted rainfall অনুযায়ী সেচ কমবে কিনা

        - 💧 আগে থেকে থাকা পানি বিবেচনা

        - 🟫 মাটির ধরন অনুযায়ী পানি

        - 🌱 crop growth stage অনুযায়ী পানি

        - 💨 ET0 অনুযায়ী পানির চাহিদা

        - 🚿 irrigation efficiency অনুযায়ী সেচ


        ---


        ### 🤖 Machine Learning

        এই system CatBoost Regression model ব্যবহার করে
        daily rainfall prediction করে।


        ---


        ### 👨‍💻 Developed By

        **Shams, Tasrif & Jishan**

        """

    )



# END OF FILE

#
# FINAL DEVELOPER MAP
#
# [01] Imports
#
# [02] show_about()
#       │
#       ├── [03] About Page Title
#       │
#       └── [04] About Page Content
#             │
#             ├── [04-A] Rainfall Prediction System
#             ├── [04-B] Smart Agriculture System
#             ├── [04-C] Machine Learning
#             └── [04-D] Developed By