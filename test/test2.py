import pandas as pd
import altair as alt
import streamlit as st
import math
from datetime import datetime

df = pd.read_csv("./conjuntaRecortadaToCSV.csv")


date = datetime.now()
currentDate = pd.Period(date.today().isoformat(),'M')  
currentyear = currentDate.year

df["age"] = currentyear-df["year"]

max = df["age"].max()
min = df["age"].min()
ageOptions = list(range(min,max+1))

gendersList = ["all", "male", "female"]

genderFilter = st.sidebar.selectbox("chosse gender", gendersList)

ageSlider = st.sidebar.slider("chosse age range", min_value=min, max_value=max, value=[min, max])


if genderFilter != "all":
    df=df[df["gender"] == genderFilter]

df = df[df["age"] >=ageSlider[0]]
df = df[df["age"] <=ageSlider[1]]

totalCountPatients= df.shape[0]
# pagination
limitList = [5,10, 20 ,50, 100]
limit = st.sidebar.select_slider("choose limit page", limitList)
paginasList =list(range(1,math.ceil(totalCountPatients/limit)+1))


df["position"] = df.reset_index().index

patientPagination = st.sidebar.selectbox("chosse patient page", paginasList)
skip = (patientPagination-1)*limit
pageMax = df[df["position"] <= skip+limit-1]
page = pageMax[pageMax["position"]>= skip]

point = alt.selection_point()

palette = ["#f86","#f56","#f23","#8f6","#5f6","#2f3","#972","#86f","#56f","#23f"]
graf1 = alt.Chart(page).mark_bar().encode(
    x=alt.X("_id:N"),
    y=alt.Y("age:Q"),
    tooltip=["gender","geoLocationInfo"],
    color = alt.Color("_id:N", scale=alt.Scale(range=palette))
).properties(title = "Patients")


st.altair_chart(graf1, use_container_width=True)
totalPatientText = "Total pacientes: "+ str(totalCountPatients)
st.text(totalPatientText)

