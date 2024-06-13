import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime
import json
from files.icd10 import  icd10
from files.icd9 import  icd9
from files.icdGroups import icdGroup
from files.ndc import  ndc
from files.analytics import analitycs
import random
from mongo.mongo_service import MongoService
from mongo.mongo_connection import conjuntaIACollection

st.set_page_config(page_title="HIGIA", layout = "wide")

# CONNECTION

bbdd = MongoService(conjuntaIACollection)


#SIDEBAR
st.sidebar.image("./images/logo.png")
id = st.sidebar.text_input("introduce el id", placeholder="introduce el id", label_visibility="hidden", value="Patient_230159_1")

ids = ["","Patient_230261_1", "Patient_230159_1","Patient_441146_1",]
id2 = st.sidebar.selectbox("Patient id", ids)

if id2 != "":
    id =id2


patient =bbdd.findById(id)



#HEADER
st.header("PATIENT RISK ANALYSYS", divider='grey')


# PATIENT INFO
date = datetime.now()
currentDate = pd.Period(date.today().isoformat(),'M')  
currentyear = currentDate.year

age = currentyear-patient["year"]
gender = patient["gender"]
source = patient["sourceData"]
locationDict = patient["geoLocationInfo"]

location = ""
for key in locationDict:
    info = locationDict[key]
    if info != "":
        toAdd = key+": "+locationDict[key]
        location = location+"\n"+toAdd


#ENCOUNTERS
encounters = patient["encounters"]

#DIAGS

diags = set()

for encounter in encounters:
    for key in encounter["DIAG"]:
        diags.add(str(key))

diagsText = ""
for key in diags:
    if key in icd10:
        diagsText= diagsText+"\n"+str(key)+": "+icd10[key]
    elif key in icdGroup:
        diagsText= diagsText+"\n"+str(key)+": "+icdGroup[key]
    elif key in icd9:
        diagsText= diagsText+"\n"+str(key)+": "+icd9[key]
    else: 
        print(key+ "no encontrada")
        pass

# DRUGS

drugs = set()

for encounter in encounters:
    for drug in encounter["MEDS"]:
        if str(drug) != "0000":
            drugs.add(str(drug))


drugsText = ""
for drug in drugs:
    drugsText= drugsText+"\n"+str(drug)+": "+ndc[drug]


col3, col4= st.columns([0.3 ,0.7])
with col3:
    with st.container(border=True):
        st.subheader("Patient info")
        st.text("patient: "+patient["_id"]+"\ngender:"+gender+"\nage:"+str(age)+"\nsource:"+source+location)
        #st.html("</br>")
        st.subheader("Diagnoses")
        if diagsText == "":
            diagsText = "Diagnoses info does not exist"
        st.text(diagsText)
        #st.html("</br>")
        st.subheader("Drugs")
        if drugsText == "":
            drugsText = "Drugs info Does not exist"
        st.text(drugsText)

analisisList = ['PHO', 'DEN', 'GO', 'PO', 'BILO', 'UROO', 'ACEO', 'NITO', 'HEMO', 'LEUO', 'GS', 'CT', 'TG', 'HEM', 'HB', 'HCTO', 'VCM', 'HCM', 'CHCM', 'RDW', 'LEUC', 'NEUT', 'LINF%', 'MONO', 'EOS', 'BASO', 'LINF', 'PLQ', 'VMP', 'AU', 'CTI', 'GOT', 'GPT', 'GGT']

analisis= {}

for a in analisisList:
    analisis[a] =[]

for encounter in encounters:
   for key in encounter["LABS"]:
        if str(key) != "0000":
            try:
                value = float(encounter["LABS"][key]["value"])
            except:
                value = 0
            analisisDate = {
                "date": encounter["date"].split(" ")[0],
                "value": value,
                "unit": encounter["LABS"][key]["unit"]
            }
            analisis[analitycs[key]].append(analisisDate)

with col4:
    with st.container(border=True):
        st.subheader("Analysis")
        col6, col7, col8= st.columns(3)
        with col6:
            chossedAnalisis1  = st.selectbox("chosse analisis 1", analisisList, label_visibility="hidden")
            analisisSeries1 = analisis[chossedAnalisis1]
            if len(analisisSeries1) > 0:
                unit1 = analisisSeries1[0]["unit"]
                analisisData1 = pd.DataFrame(analisisSeries1)
                graf1 = alt.Chart(analisisData1).mark_line().encode(
                    x=alt.X("date:N"),
                    y=alt.Y("value:Q"),
                ).properties(title = unit1)
                st.altair_chart(graf1.properties(width= "container"), use_container_width=True)
            else:
                st.text(chossedAnalisis1+" info does not exist")

        with col7:
            chossedAnalisis2  = st.selectbox("chosse analisis 2", analisisList, label_visibility="hidden")
            analisisSeries2 = analisis[chossedAnalisis2]
            if len(analisisSeries2) > 0:
                unit2= analisisSeries2[0]["unit"]
                analisisData2 = pd.DataFrame(analisisSeries2)
                graf2 = alt.Chart(analisisData2).mark_line().encode(
                    x=alt.X("date:N"),
                    y=alt.Y("value:Q"),
                ).properties(title = unit2)
                st.altair_chart(graf2.properties(width= "container"), use_container_width=True)
            else:
                st.text(chossedAnalisis2+" info does not exist")

        with col8:
            chossedAnalisis3  = st.selectbox("chosse analisis 3", analisisList, label_visibility="hidden")
            analisisSeries3 = analisis[chossedAnalisis3]
            if len(analisisSeries3) > 0:
                unit3= analisisSeries3[0]["unit"]
                analisisData3 = pd.DataFrame(analisisSeries3)
                graf3 = alt.Chart(analisisData2).mark_line().encode(
                    x=alt.X("date:N"),
                    y=alt.Y("value:Q"),
                ).properties(title = unit3)
                st.altair_chart(graf3.properties(width= "container"), use_container_width=True)
            else:
                st.text(chossedAnalisis3+" info does not exist")

with st.container(border=True):
    st.subheader("Predictions")
    # FALSE INFO FOR CIRCLES
    # diabetes
    diabetesPercentaje = random.uniform(0.0, 1.0)

    # dislipidemia
    dislipedemiaPercentaje = random.uniform(0.0, 1.0)

    # obesity
    obesityPercentaje = random.uniform(0.0, 1.0)

    # NASH
    nashPercentaje = random.uniform(0.0, 1.0)

    # kidney disease
    kidneyDiseasePercentaje = random.uniform(0.0, 1.0)

    # heart disease
    heartDiseasePercentaje = random.uniform(0.0, 1.0)

    col9, col10 = st.columns(2)
    col11, col12 = st.columns(2)
    col13, col14= st.columns(2)

    def getPercentajePalette(value):
        # PALETTE COLOURS
        high="#FF0000"
        middel= "#E3600F" 
        midlow = "#FFFA00"
        low = "#1FFF00"

        circleColor="#E3E4E2"

        if value < 0.25:
            return [low, circleColor]
        elif value < 0.5:
            return [midlow, circleColor]
        elif value < 0.75:
            return [middel, circleColor]
        else:
            return [high, circleColor]


    # diabetesPercentaje
    with col9:
        if diabetesPercentaje > 0:
            noDiabetesPercentaje = 1-diabetesPercentaje
            diabetesPercentajeSource = pd.DataFrame({"category": ["diabetes", "noDiabetes"], "value": [diabetesPercentaje, noDiabetesPercentaje]})

            percentajePalete = getPercentajePalette(diabetesPercentaje)

            graf4 = alt.Chart(diabetesPercentajeSource).mark_arc(
                radius=50,
                radius2=100
            ).encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color = alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            ).properties(title = "Diabetes")

            st.altair_chart(graf4, use_container_width=True)
        else:
            st.text("Diabetes undiagnosed")

    #dislipedemiaPercentaje
    with col10:
        if dislipedemiaPercentaje > 0:
            nodislipedemiaPercentaje = 1-dislipedemiaPercentaje
            dislipedemiaPercentajeSource = pd.DataFrame({"category": ["dislipidemia", "noDislipidemia"], "value": [dislipedemiaPercentaje, nodislipedemiaPercentaje]})

            percentajePalete = getPercentajePalette(dislipedemiaPercentaje)

            graf5 = alt.Chart(dislipedemiaPercentajeSource).mark_arc(
                radius=50,
                radius2=100
            ).encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color = alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            ).properties(title = "Dislipidemia")

            st.altair_chart(graf5, use_container_width=True)
        else:
            st.text("Dislipidemia undiagnosed")

    #obesityPercentaje
    with col11:
        if obesityPercentaje > 0:
            noobesityPercentaje = 1-obesityPercentaje
            obesityPercentajeSource = pd.DataFrame({"category": ["Obesity", "noObesity"], "value": [obesityPercentaje, noobesityPercentaje]})

            percentajePalete = getPercentajePalette(obesityPercentaje)

            graf7 = alt.Chart(obesityPercentajeSource).mark_arc(
                radius=50,
                radius2=100
            ).encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color = alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            ).properties(title = "Obesity")

            st.altair_chart(graf7, use_container_width=True)

        else:
            st.text("Obesity undiagnosed")

    # nashPercentaje
    with col12:
        if nashPercentaje > 0:
            nonashPercentaje = 1-nashPercentaje
            nashPercentajeSource = pd.DataFrame({"category": ["nash", "noNash"], "value": [nashPercentaje, nonashPercentaje]})

            percentajePalete = getPercentajePalette(nashPercentaje)

            graf7 = alt.Chart(nashPercentajeSource).mark_arc(
                radius=50,
                radius2=100
            ).encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color = alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            ).properties(title = "Nash")

            st.altair_chart(graf7, use_container_width=True)
        else:
            st.text("Nash undiagnosed")

    # kidneyDiseasePercentaje
    with col13:
        if kidneyDiseasePercentaje > 0:
            nokidneyDiseasePercentaje = 1-kidneyDiseasePercentaje
            kidneyDiseasePercentajeSource = pd.DataFrame({"category": ["kidneyDisease", "noKidneyDisease"], "value": [kidneyDiseasePercentaje, nokidneyDiseasePercentaje]})

            percentajePalete = getPercentajePalette(kidneyDiseasePercentaje)

            graf8 = alt.Chart(kidneyDiseasePercentajeSource).mark_arc(
                radius=50,
                radius2=100
            ).encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color = alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            ).properties(title = "Kidney disease")

            st.altair_chart(graf8, use_container_width=True)
        else:
            st.text("Kidney disease undiagnosed")

    # heartDiseasePercentaje
    with col14:
        if heartDiseasePercentaje > 0:
            noheartDiseasePercentaje = 1-heartDiseasePercentaje
            heartDiseasePercentajeSource = pd.DataFrame({"category": ["heartDisease", "noHeartDisease"], "value": [heartDiseasePercentaje, noheartDiseasePercentaje]})

            percentajePalete = getPercentajePalette(heartDiseasePercentaje)

            graf9 = alt.Chart(heartDiseasePercentajeSource).mark_arc(
                radius=50,
                radius2=100
            ).encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color = alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            ).properties(title = "Heart disease")

            st.altair_chart(graf9, use_container_width=True)
        else:
            st.text("Heart disease undiagnosed")


