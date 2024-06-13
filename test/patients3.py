import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime
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
with st.sidebar:
    ## LOGO  st-emotion-cache-1v0mbdj e115fcil1
    
    st.html("""
        <style>
            [data-testid=stSidebar] [data-testid=stImage]{
                text-align: center;
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 100%;
            }
        </style>
        """)
    
    
    st.image("./images/logo.png", width=140)
    ## FILTERS
    st.divider()
    id = st.text_input("introduce el id", placeholder="introduce el id", label_visibility="hidden", value="Patient_230159_1")

    ids = ["","Patient_230261_1", "Patient_230159_1","Patient_441146_1",]
    id2 = st.selectbox("Patient id", ids)

    if id2 != "":
        id =id2


    patient =bbdd.findById(id)



#HEADER
CH1, CH2 = st.columns([7, 1])
with CH1:
    st.header("PATIENT RISK ANALYSYS")  # usa markdown ,cuando esot es una bacera , es por algun motivo?
with CH2:
    st.image("images/flag.png", width=100)


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


#ENCOUNTERS_INFO
encounters = patient["encounters"]

#DIAGS_INFO

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

# DRUGS_INFO

drugs = set()

for encounter in encounters:
    for drug in encounter["MEDS"]:
        if str(drug) != "0000":
            drugs.add(str(drug))


drugsText = ""
for drug in drugs:
    drugsText= drugsText+"\n"+str(drug)+": "+ndc[drug]

# ANALYSIS_INFO
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

CInfo, CgrafsAnalysis= st.columns([3 ,7])
with CInfo:
    with st.container(border=True, height= 533):
        st.subheader("Patient info")
        st.text("patient: "+patient["_id"]+"\ngender:"+gender+"\nage:"+str(age)+"\nsource:"+source+location)
        st.subheader("Diagnoses")
        if diagsText == "":
            diagsText = "Diagnoses info does not exist"
        st.text(diagsText)
        st.subheader("Drugs")
        if drugsText == "":
            drugsText = "Drugs info Does not exist"
        st.text(drugsText)

with CgrafsAnalysis:
    with st.container(border=True):
        st.subheader("Analysis")
        CAnalisisData1, CAnalisisData2, CAnalisisData3= st.columns(3)
        with CAnalisisData1:
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

        with CAnalisisData2:
            defaultIndex2 = analisisList.index("GS")
            chossedAnalisis2  = st.selectbox("chosse analisis 2", analisisList, label_visibility="hidden", index=defaultIndex2)
            analisisSeries2 = analisis[chossedAnalisis2]
            if len(analisisSeries2) > 0:
                unit2= analisisSeries2[0]["unit"]
                analisisData2 = pd.DataFrame(analisisSeries2)
                graf2 = alt.Chart(analisisData2).mark_line().encode(
                    x=alt.X("date:N"),
                    y=alt.Y("value:Q")
                ).properties(title = unit2)
                st.altair_chart(graf2.properties(width= "container"), use_container_width=True)
            else:
                st.text(chossedAnalisis2+" info does not exist")

        with CAnalisisData3:
            defaultIndex3 = analisisList.index("HEMO")
            chossedAnalisis3  = st.selectbox("chosse analisis 3", analisisList, label_visibility="hidden", index=defaultIndex3)
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

    CDiabetes, CDislipidemia = st.columns(2)
    CObesity, CNash = st.columns(2)
    CKidney, CHeart= st.columns(2)    

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
    with CDiabetes:
        if diabetesPercentaje > 0:
            
            noDiabetesPercentaje = 1-diabetesPercentaje
            diabetesPercentajeSource = pd.DataFrame({"category": ["diabetes", "noDiabetes"], "value": [diabetesPercentaje, noDiabetesPercentaje]})

            percentajePalete = getPercentajePalette(diabetesPercentaje)

            diabetesBase = alt.Chart(diabetesPercentajeSource).encode(
                alt.Theta("value:Q").stack(True),
                alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            )

            text = diabetesBase.mark_text(radius=0, size=50).encode(text=alt.Text("value:Q", format=".0%"), ).transform_filter(
                alt.datum.category=="diabetes",
            )

          
            diabetes_arc = diabetesBase.mark_arc(
                radius=80,
                radius2=100,

            ).properties(title = alt.TitleParams("Diabetes", anchor='middle', frame='bounds'))

            st.altair_chart(diabetes_arc+text, use_container_width=True)
            
        else:
            st.text("Diabetes undiagnosed")

    #dislipedemiaPercentaje
    with CDislipidemia:
        if dislipedemiaPercentaje > 0:
            nodislipedemiaPercentaje = 1-dislipedemiaPercentaje
            dislipedemiaPercentajeSource = pd.DataFrame({"category": ["dislipidemia", "noDislipidemia"], "value": [dislipedemiaPercentaje, nodislipedemiaPercentaje]})

            percentajePalete = getPercentajePalette(dislipedemiaPercentaje)

            dislipidemiaBase = alt.Chart(dislipedemiaPercentajeSource).encode(
                alt.Theta("value:Q").stack(True),
                alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            )

            text = dislipidemiaBase.mark_text(radius=0, size = 50).encode(text=alt.Text("value:Q", format=".0%"), ).transform_filter(
                alt.datum.category=="dislipidemia",
            )

            dislipidemia_arc = dislipidemiaBase.mark_arc(
                radius=80,
                radius2=100
            ).properties(title = alt.TitleParams("Dislipidemia", anchor='middle', frame='bounds'))

            st.altair_chart(dislipidemia_arc + text, use_container_width=True)
        else:
            st.text("Dislipidemia undiagnosed")

    #obesityPercentaje
    with CObesity:
        if obesityPercentaje > 0:
            noobesityPercentaje = 1-obesityPercentaje
            obesityPercentajeSource = pd.DataFrame({"category": ["Obesity", "noObesity"], "value": [obesityPercentaje, noobesityPercentaje]})

            percentajePalete = getPercentajePalette(obesityPercentaje)

            obesityBase = alt.Chart(obesityPercentajeSource).encode(
                alt.Theta("value:Q").stack(True),
                alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            )

            text = obesityBase.mark_text(radius=0, size = 50).encode(text=alt.Text("value:Q", format=".0%"), ).transform_filter(
                alt.datum.category=="Obesity",
            )

            obesity_arc = obesityBase.mark_arc(
                radius=80,
                radius2=100
            ).properties(title = alt.TitleParams("Obesity", anchor='middle', frame='bounds'))

            st.altair_chart(obesity_arc + text, use_container_width=True)

        else:
            st.text("Obesity undiagnosed")

    # nashPercentaje
    with CNash:
        if nashPercentaje > 0:
            nonashPercentaje = 1-nashPercentaje
            nashPercentajeSource = pd.DataFrame({"category": ["nash", "noNash"], "value": [nashPercentaje, nonashPercentaje]})

            percentajePalete = getPercentajePalette(nashPercentaje)

            nashBase = alt.Chart(nashPercentajeSource).encode(
                alt.Theta("value:Q").stack(True),
                alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            )

            text = nashBase.mark_text(radius=0, size = 50).encode(text=alt.Text("value:Q", format=".0%"), ).transform_filter(
                alt.datum.category=="nash",
            )

            nash_arc = nashBase.mark_arc(
                radius=80,
                radius2=100
            ).properties(title = alt.TitleParams("Nash", anchor='middle', frame='bounds'))

            st.altair_chart(nash_arc + text, use_container_width=True)
        else:
            st.text("Nash undiagnosed")

    # kidneyDiseasePercentaje
    with CKidney:
        if kidneyDiseasePercentaje > 0:
            nokidneyDiseasePercentaje = 1-kidneyDiseasePercentaje
            kidneyDiseasePercentajeSource = pd.DataFrame({"category": ["kidneyDisease", "noKidneyDisease"], "value": [kidneyDiseasePercentaje, nokidneyDiseasePercentaje]})

            percentajePalete = getPercentajePalette(kidneyDiseasePercentaje)

            kidneyBase = alt.Chart(kidneyDiseasePercentajeSource).encode(
                alt.Theta("value:Q").stack(True),
                alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            )

            text = kidneyBase.mark_text(radius=0, size = 50).encode(text=alt.Text("value:Q", format=".0%"), ).transform_filter(
                alt.datum.category=="kidneyDisease",
            )

            kidney_arc = kidneyBase.mark_arc(
                radius=80,
                radius2=100
            ).properties(title = alt.TitleParams("Kidney disease", anchor='middle', frame='bounds'))

            st.altair_chart(kidney_arc + text, use_container_width=True)
        else:
            st.text("Kidney disease undiagnosed")

    # heartDiseasePercentaje
    with CHeart:
        if heartDiseasePercentaje > 0:
            noheartDiseasePercentaje = 1-heartDiseasePercentaje
            heartDiseasePercentajeSource = pd.DataFrame({"category": ["heartDisease", "noHeartDisease"], "value": [heartDiseasePercentaje, noheartDiseasePercentaje]})

            percentajePalete = getPercentajePalette(heartDiseasePercentaje)

            heartBase = alt.Chart(heartDiseasePercentajeSource).encode(
                alt.Theta("value:Q").stack(True),
                alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
            )

            text = heartBase.mark_text(radius=0, size = 50).encode(text=alt.Text("value:Q", format=".0%"), ).transform_filter(
                alt.datum.category=="heartDisease",
            )

            heart_arc = heartBase.mark_arc(
                radius=80,
                radius2=100
            ).properties(title = alt.TitleParams("Heart disease", anchor='middle', frame='bounds'))

            st.altair_chart(heart_arc + text, use_container_width=True)
        else:
            st.text("Heart disease undiagnosed")


