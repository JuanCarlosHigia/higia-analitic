import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime
from files.icd10 import  icd10
from files.icd9 import  icd9
from files.icdGroups import icdGroup
from files.ndc import  ndc
from files.analytics import analytics
import random
from mongo.mongo_service import MongoService
from mongo.mongo_connection import mongoCollection
import math

st.set_page_config(page_title="HIGIA", layout = "wide")

# CONNECTION
bbdd = MongoService(mongoCollection)

# CSS

st.html("""
        <style>
            [data-testid=stSidebar] [data-testid=stImage]{
                text-align: center;
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 100%;
            },
            body {
                font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;
            }
        </style>
        """)

#SIDEBAR
with st.sidebar:
    ## LOGO 
    st.image("./images/logo.png", width=140)

    ## COMMON METHODS
    def getCurrentYear():
        date = datetime.now()
        currentDate = pd.Period(date.today().isoformat(),'M')  
        currentyear = currentDate.year
        return currentyear
    
    def update_pagination_filters():
        currentyear= getCurrentYear()
        minYear= currentyear- st.session_state.Age[0]
        maxYear=currentyear- st.session_state.Age[1]
        # totalList = bbdd.getTotalLists(st.session_state.patient_id_regex,-1, 0, st.session_state.nationality, st.session_state.source, minYear, maxYear, st.session_state.gender)
        totalList = bbdd.getTotalLists(st.session_state.patient_id_regex,-1, 100, 
                                                          st.session_state.nationality, st.session_state.source
                                                          ,minYear, maxYear, st.session_state.gender)
        if "total_Patients" not in st.session_state:
            nationalites= set()
            sources = set()
            for item in totalList:
                nationalites.add(item["geoLocationInfo"]["nationality"])
                sources.add(item["sourceData"])
            nationalitesList  = list(nationalites)
            nationalitesListClean= sorted([item for item in nationalitesList if item])
            nationalitesListClean.insert(0, "All")
            st.session_state.nationalites = list(nationalitesListClean)

            
            sourceList = list(sources)
            sourceListClean= [item for item in sourceList if item]
            sourceListClean.insert(0, "All")
            st.session_state.sources = sorted(list(sourceListClean))

        st.session_state.total_Patients = len(totalList)

        st.session_state.nationalityIndex = st.session_state.nationalites.index(st.session_state.nationality)
        st.session_state.sourceIndex = st.session_state.sources.index(st.session_state.source)
  

    def create_patientList():
        update_pagination_filters()
        currentyear= getCurrentYear()
        minYear= currentyear- st.session_state.Age[0]
        maxYear=currentyear- st.session_state.Age[1]
        st.session_state.skip = (st.session_state.page_num -1)*st.session_state.limit
        st.session_state.patients_list = bbdd.getPatients(st.session_state.patient_id_regex,st.session_state.skip, st.session_state.limit, 
                                                          st.session_state.nationality, st.session_state.source
                                                          ,minYear, maxYear, st.session_state.gender)
        
        if len(st.session_state.patients_list)> 0:
            st.session_state.patient_id=st.session_state.patients_list[0]
            st.session_state.patients_list_index=0
        st.session_state.page_num=1

    ## INITIAL STATE
    if 'refresh' not in st.session_state:
        st.session_state.refresh = 0
    if "patient_id" not in st.session_state:
        st.session_state.patient_id = ""

    if "nationality" not in st.session_state:
        st.session_state.nationality = "All"
    
    if "Age" not in st.session_state:
        st.session_state.Age=[1, 100]

    if "limit" not in st.session_state:
        st.session_state.limit = 20
    
   
    if "page_num" not in st.session_state:
        st.session_state.page_num = 1

    if "source" not in st.session_state:
        st.session_state.source = "All"
    
    if "gender" not in st.session_state:
        st.session_state.gender = "All"
    
    if "patient_id_regex" not in st.session_state:
        st.session_state.patient_id_regex = ""
    
    st.session_state.skip = (st.session_state.page_num -1)*st.session_state.limit
    if "patients_list_index" not in st.session_state:
        st.session_state.patients_list_index=0
    if "patients_list" not in st.session_state:
        create_patientList()
    total_pages = math.ceil(st.session_state.total_Patients/st.session_state.limit)
    ## PATIENT SELECTOR
    st.divider()
    st.session_state.patient_id=st.selectbox("Patients List", options=st.session_state.patients_list, index= st.session_state.patients_list_index)

    ## PATIENT FILTERS
    st.divider()
    st.text_input("Search Match", key="patient_id_regex")
    st.selectbox("Source", options=st.session_state.sources, key="source", index=st.session_state.sourceIndex)
    st.selectbox("Nationality", options=st.session_state.nationalites, key="nationality", index=st.session_state.nationalityIndex)
    st.selectbox("Gender", options=["All", "male", "female"], key="gender")
    st.slider("Age", min_value=1, max_value=100, key="Age")
    
    ### FILTER BUTTON
    st.button("Add Filters", on_click=create_patientList, type="primary")
    
        
    ## PAGINATION
    st.divider()
    st.select_slider("Number of patients", options=[5,10,15,20,50], key="limit", on_change=create_patientList)
    cPage0, cPage1 = st.columns([6,1])
    with cPage0:
        st.number_input("Pages", min_value=1, max_value=total_pages, step=1,key="page_num", on_change=create_patientList)
    with cPage1:
        st.html("<p style='margin-top: 38px; margin-left:-10px;'>/ "+str(total_pages)+"</p>")

    

  
# BODY

## HEADER
CH1, CH2 = st.columns([7, 1])
with CH1:
    st.header("PATIENT RISK ANALYSYS")  # usa markdown ,cuando esot es una bacera , es por algun motivo?
with CH2:
    st.image("images/flag.png", width=100)


## PATIENT INFO
if len(st.session_state.patients_list)>0:
    patient = bbdd.findById(st.session_state.patient_id)
    currentyear= getCurrentYear()

    age = currentyear-patient["year"]
    gender = patient["gender"]
    source = patient["sourceData"]
    locationDict = patient["geoLocationInfo"]

    location = ""
    for key in locationDict:
        info = locationDict[key]
        if info != "":
            toAdd = key.capitalize()+": "+locationDict[key]
            location = location+"\n"+toAdd


    ## ENCOUNTERS_INFO
    encounters = patient["encounters"]

    ## DIAGS_INFO

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
            pass

    ## DRUGS_INFO

    drugs = set()

    for encounter in encounters:
        for drug in encounter["MEDS"]:
            if str(drug) != "0000":
                drugs.add(str(drug))


    drugsText = ""
    for drug in drugs:
        drugsText= drugsText+"\n"+str(drug)+": "+ndc[drug]

    ## PREDICTIONS
    CInfo, CPredictions= st.columns([3 ,7])
    maxHeight = 823
    with CInfo:
        #with st.container(border=True, height= 533):
        
        with st.container(border=True, height= maxHeight):
            st.subheader("Patient Info")
            st.text("Patient: "+patient["_id"]+"\nGender:"+gender.capitalize()+"\nAge:"+str(age)+"\nSource:"+source+location)
            st.subheader("Diagnoses")
            if diagsText == "":
                diagsText = "Diagnoses info does not exist"
            st.text(diagsText)
            st.subheader("Drugs")
            if drugsText == "":
                drugsText = "Drugs info Does not exist"
            st.text(drugsText)

    with CPredictions:
        def getLabel(value):
                if value > 0.25 and value < 0.75:
                    newvalue= int(value*100)

                    return str(newvalue)+"%"
                elif value <= 0.25:
                    return "LOW RISK"
                else:
                    return "HIGH RISK"
        with st.container(border=True, height= maxHeight):
            st.subheader("Predictions")
            # FALSE INFO FOR CIRCLES
            # diabetes
            diabetesPercentaje = random.uniform(0.8, 0.9)
            noDiabetesPercentaje = 1-diabetesPercentaje

           



            diabetesPD = {
                "category": ["diabetes", "noDiabetes"], 
                "value": [diabetesPercentaje, noDiabetesPercentaje],
                 "text": [getLabel(diabetesPercentaje), getLabel(diabetesPercentaje)]
            }
            

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

            CDiabetes, CDislipidemia,CObesity = st.columns(3)
            CNash, CKidney, CHeart= st.columns(3)    

            def getPercentajePalette(value):
                # PALETTE COLOURS
                high="#f35261"
                middel="#fbcd78"  
                midlow = "#00b888"
                low = "#d5dbca"

                circleColor="#d5dbca"

                if value < 0.25:
                    return [low, circleColor]
                elif value < 0.5:
                    return [midlow, circleColor]
                elif value < 0.75:
                    return [middel, circleColor]
                else:
                    return [high, circleColor]
            
            def getPercentajePaletteText(value):
                # PALETTE COLOURS
                high="#f35261"
                middel="#fbcd78"  
                midlow = "#00b888"
    


                if value < 0.25:
                    return [midlow, midlow]
                elif value < 0.5:
                    return [middel, middel]
                elif value < 0.75:
                    return [middel, middel]
                else:
                    return [high, high]
                
            


            # diabetesPercentaje
            with CDiabetes:
                if diabetesPercentaje > 0:
                
                    diabetesPercentajeSource = pd.DataFrame(diabetesPD)

                    percentajePalete = getPercentajePalette(diabetesPercentaje)
                    percentajePaleteText = getPercentajePaletteText(diabetesPercentaje)

                    diabetesBase = alt.Chart(diabetesPercentajeSource).encode(
                        theta=alt.Theta("value:N").stack(True),
                        color=alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
                    )


                    text = alt.Chart(diabetesPercentajeSource).mark_text(fontSize=30).encode(
                        text="text:N",
                        color=alt.Color("text:N", legend=None, scale=alt.Scale(range=percentajePaleteText))
                    )

                
                    diabetes_arc = diabetesBase.mark_arc(
                        radius=80,
                        radius2=100,

                    ).properties(title = alt.TitleParams("Diabetes", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

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
                    ).properties(title = alt.TitleParams("Dislipidemia", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

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
                    ).properties(title = alt.TitleParams("Obesity", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

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
                    ).properties(title = alt.TitleParams("Nash", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

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
                    ).properties(title = alt.TitleParams("Kidney disease", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

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
                    ).properties(title = alt.TitleParams("Heart disease", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

                    st.altair_chart(heart_arc + text, use_container_width=True)
                else:
                    st.text("Heart disease undiagnosed")

    # ANALYSIS_INFO
    analisisList = []
    for analyticKey in analytics:
        analisisList.append(analytics[analyticKey]["label"])

    analisis= {}

    bloodPressure =[]

    for a in analisisList:
        analisis[a] =[]

    for encounter in encounters:
        for key in encounter["LABS"]:
            if str(key) != "0000" and key in analytics:
                try:
                    value = float(encounter["LABS"][key]["value"])
                except:
                    value = 0
                if value > 0:
                    unit = encounter["LABS"][key]["unit"]
                    if unit == "":
                        unit = " "    
                    analisisData = {
                        "date": encounter["date"].split(" ")[0],
                        "type": "value",
                        "value": value,
                        "unit": unit
                    }
                    analisis[analytics[key]["label"]].append(analisisData)
                    maxValue = 0
                    minValue = 0
                    if analytics[key]["max"] != "":
                        maxValue =  analytics[key]["max"]
                        minValue =  analytics[analyticKey]["min"]
                    analisismax = {
                        "date": encounter["date"].split(" ")[0],
                        "type": "max",
                        "value": maxValue,
                        "unit": unit
                    }
                    analisis[analytics[key]["label"]].append(analisismax)
                    analisisMin = {
                        "date": encounter["date"].split(" ")[0],
                        "type": "min",
                        "value": minValue,
                        "unit": unit
                    }
                    analisis[analytics[key]["label"]].append(analisisMin)

        for key in encounter["PHYS"]:
            if key == "BloodPressure(high)":
                value = float(encounter["PHYS"]["BloodPressure(high)"]["value"])
                if value > 0:
                    date = encounter['date'].split(" ")[0]
                    unit = encounter["PHYS"]["BloodPressure(high)"]["unit"]
                    bloodPressureData ={
                        "value":value,
                        "type":"high",
                        "unit":unit,
                        "date": date
                    }
                    bloodPressure.append(bloodPressureData)
                    maxLimit ={
                        "value":120,
                        "type":"max",
                        "unit":unit,
                        "date": date
                    }
                    bloodPressure.append(maxLimit)
            if key == "BloodPressure(low)":
                value = float(encounter["PHYS"]["BloodPressure(low)"]["value"])
                if value > 0:
                    unit = encounter["PHYS"]["BloodPressure(low)"]["unit"]
                    bloodPressureData ={
                        "value":value,
                        "type":"low",
                        "unit":unit,
                        "date": date
                    }
                    bloodPressure.append(bloodPressureData)
                    minLimit ={
                        "value":80,
                        "type":"min",
                        "unit":unit,
                        "date": date
                    }
                    bloodPressure.append(minLimit)

    with st.container(border=True):
        st.subheader("Analysis")
        fixData, CAnalisisData1, CAnalisisData2, CAnalisisData3= st.columns(4)
        with fixData:
            if len(bloodPressure) > 0:
                highData0 = pd.DataFrame(bloodPressure)
                palette = ["#2F7BE5","#10ACE6","#E62A27","#F78A66"]
                graf0 = alt.Chart(highData0).mark_line().encode(
                    x=alt.X("date:N"),
                    y=alt.Y("value:Q"),
                    color=alt.Color("type:N", scale=alt.Scale(range=palette))
                )
                st.html("<p>Blood Pressure</p></br></br></br>")
                st.altair_chart(graf0.properties(width= "container"), use_container_width=True)
            else:
                st.markdown("<div style='text-align: center; padding-top: 150px;'>No pressure data</div>", unsafe_allow_html=True)
        palette = ["#E62A27","#F78A66","#2F7BE5"]
        with CAnalisisData1:
            chossedAnalisis1  = st.selectbox("chosse analisis 1", analisisList, label_visibility="hidden")
            analisisSeries1 = analisis[chossedAnalisis1]
            if len(analisisSeries1) > 0:
                unit1 = analisisSeries1[0]["unit"]
                analisisData1 = pd.DataFrame(analisisSeries1)
                
                graf1 = alt.Chart(analisisData1).mark_line().encode(
                    x=alt.X("date:N"),
                    y=alt.Y("value:Q"),
                    color=alt.Color("type:N", scale=alt.Scale(range=palette))
                ).properties(title = unit1)
                st.altair_chart(graf1.properties(width= "container"), use_container_width=True)
            else:
                st.text(chossedAnalisis1+" info does not exist")

        with CAnalisisData2:

            chossedAnalisis2  = st.selectbox("chosse analisis 2", analisisList, label_visibility="hidden", index=1)
            analisisSeries2 = analisis[chossedAnalisis2]
            if len(analisisSeries2) > 0:
                unit2= analisisSeries2[0]["unit"]
                analisisData2 = pd.DataFrame(analisisSeries2)
                graf2 = alt.Chart(analisisData2).mark_line().encode(
                    x=alt.X("date:N"),
                    y=alt.Y("value:Q"),
                    color=alt.Color("type:N", scale=alt.Scale(range=palette))
                ).properties(title = unit2)
                st.altair_chart(graf2.properties(width= "container"), use_container_width=True)
            else:
                st.text(chossedAnalisis2+" info does not exist")

        with CAnalisisData3:
            chossedAnalisis3  = st.selectbox("chosse analisis 3", analisisList, label_visibility="hidden", index=2)
            analisisSeries3 = analisis[chossedAnalisis3]
            if len(analisisSeries3) > 0:
                unit3= analisisSeries3[0]["unit"]
                analisisData3 = pd.DataFrame(analisisSeries3)
                graf3 = alt.Chart(analisisData3).mark_line().encode(
                    x=alt.X("date:N"),
                    y=alt.Y("value:Q"),
                    color=alt.Color("type:N", scale=alt.Scale(range=palette))
                ).properties(title = unit3)
                st.altair_chart(graf3.properties(width= "container"), use_container_width=True)
            else:
                st.text(chossedAnalisis3+" info does not exist")

else:
    st.html("<H1 style='text-align: center; margin-top:10%'>No patients found that match this criteria</H1>")

