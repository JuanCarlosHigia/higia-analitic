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
from mongo.mongo_connection import mongoCollection, pipelineCollection
import math

st.set_page_config(page_title="HIGIA", layout = "wide")

# CONNECTION
bbdd = MongoService(mongoCollection)
pipeline = MongoService(pipelineCollection)

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

        totalList = bbdd.getTotalLists(st.session_state.patient_id_regex,-1, 0, st.session_state.nationality, st.session_state.source, minYear, maxYear, st.session_state.gender)
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
            
    def check_list_status():
        if st.secrets["FORCE_UPDATE"] == "True":
            print("XXXX")
            update_pagination_filters()
            pipeline.updatePipeline(st.session_state.total_Patients, st.session_state.nationalites,st.session_state.sources)
        else:
            if "total_Patients" not in st.session_state:
                pipeline_status =  pipeline.getPipeLineStatus()
                if len(pipeline_status) == 0:
                    update_pagination_filters()
                    pipeline.updatePipeline(st.session_state.total_Patients, st.session_state.nationalites,st.session_state.sources)
                else:
                    st.session_state.total_Patients = pipeline_status[0]["total_patients"]
                    st.session_state.nationalites = pipeline_status[0]["nationality"]
                    st.session_state.sources= pipeline_status[0]["sources"]

            else:
                update_pagination_filters()

       
        
        
        st.session_state.nationalityIndex = st.session_state.nationalites.index(st.session_state.nationality)
        st.session_state.sourceIndex = st.session_state.sources.index(st.session_state.source)
  

    def create_patientList():
        check_list_status()
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

    ## DIAGS_INFO AND IMC

    diags = set()

    for encounter in encounters:
        for key in encounter["DIAG"]:
            diags.add(str(key))
        
    # diabetes, dislipidemia, obesity, nash, kidney disease, heart disease
    diagnosed= [False,False,False,False,False,False]
    
    def updateDiagnosed(keyGroup,diagnosed):
        
        if keyGroup=="O24" or keyGroup=="E08" or keyGroup=="E09" or keyGroup=="E010" or keyGroup=="E011" or keyGroup=="E013":
            diagnosed[0] =True
        elif keyGroup=="E78":
            diagnosed[1] =True
        elif keyGroup=="E66":
            diagnosed[2] =True
        elif keyGroup=="K75" or keyGroup=="K76":
            diagnosed[3] =True
        elif keyGroup=="N17" or keyGroup=="N18" or keyGroup=="N19" or keyGroup=="E08" or keyGroup=="N28":
            diagnosed[4] =True
        elif keyGroup=="I11" or keyGroup=="I13" or keyGroup=="I50" or keyGroup=="I09" or keyGroup=="I97" or keyGroup=="I20" or keyGroup=="I21" or keyGroup=="I22" or keyGroup=="I24" or keyGroup=="I25" or keyGroup=="414":
            diagnosed[5] =True   
        return diagnosed


    diagsText = ""
    for key in diags:
        if key in icd10:
            diagnosed = updateDiagnosed(key[0:3], diagnosed)
            diagsText= diagsText+"\n"+str(key)+": "+icd10[key]
        elif key in icdGroup:
            diagnosed = updateDiagnosed(key[0:3], diagnosed)
            diagsText= diagsText+"\n"+str(key)+": "+icdGroup[key]
        elif key in icd9:
            diagnosed = updateDiagnosed(key[0:3], diagnosed)
            diagsText= diagsText+"\n"+str(key)+": "+icd9[key]
        else: 
            pass

    ## DRUGS_INFO

    drugs = set()

    drugsText = ""
    for drug in drugs:
        drugsText= drugsText+"\n"+str(drug)+": "+ndc[drug]

    ## PREDICTIONS
    CInfo, CPredictions= st.columns([3 ,7])
    maxHeight = 823
    #maxHeight = 623
    with CInfo:
        
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

        with st.container(border=True, height= maxHeight):
            st.subheader("Predictions")
            # FALSE INFO FOR CIRCLES
            # diabetes
            diabetesPercentaje = random.uniform(0.0, 1.0)
    
            # dislipidemia
            dislipidemiaPercentaje = random.uniform(0.0, 1.0)

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

            
            def getPercentajePalette(value, textString=""):
                # PALETTE COLOURS
                high="#f35261"
                middel="#fbcd78"  
                midlow = "#00b888"
                low = "#d5dbca"

                circleColor="#d5dbca"

                if textString == "!Diagnosed":
                    return [middel,middel]
                elif textString == "!Undiagnosed":
                    return [high,high]
                elif value < 0.25:
                    return [low, circleColor]
                elif value < 0.5:
                    return [midlow, circleColor]
                else:
                    return [high, circleColor]
                
    
                    
            
            def getText(value, dignoased):
                if dignoased == True:
                    return "!Diagnosed"
                else:
                    if value < 0.25:
                        return "LOW RISK"
                    elif value < 0.75:
                        return str(int(value*100))+"%"
                    else:
                        return "HIGH RISK"
                
            def getTextColor(text):
                # PALETTE COLOURS
                red="#f35261"
                green = "#00b888"
    

                if text == "!Diagnosed" or text == "!Undiagnosed" or text == "HIGH RISK":
                    return red
                else:
                    if text == "LOW RISK":
                        return green
                        
                    else:
                        value = int(text[0:-1])
                        if value < 50:
                            return green
                        else: 
                            return red
            

            
            # diabetesPercentaje
            with CDiabetes:
                if diabetesPercentaje > 0:
                    diabetesSourceText={"text": [getText(diabetesPercentaje, diagnosed[0])]}
                    textString= diabetesSourceText["text"][0]
                    nodiabetesPercentaje = 1-diabetesPercentaje
                    diabetesSource = {"category": ["diabetes", "nodiabetes"], "value": [diabetesPercentaje, nodiabetesPercentaje]}
                    diabetesDataframe = pd.DataFrame(diabetesSource) 
                    diabetesTextDataframe= pd.DataFrame(diabetesSourceText)
                    percentajePalete = getPercentajePalette(diabetesPercentaje, textString)

                    diabetesBase = alt.Chart(diabetesDataframe).encode(
                        alt.Theta("value:Q").stack(True),
                        alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
                    )

                    diabetes_arc = diabetesBase.mark_arc(
                        radius=80,
                        radius2=100
                    ).properties(title = alt.TitleParams("Diabetes", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

                    text = alt.Chart(diabetesTextDataframe).mark_text(fontSize=25, color=getTextColor(textString), fontWeight="bold").encode(
                        text="text:N"
                    )

                    st.altair_chart(diabetes_arc + text, use_container_width=True)



                else:
                    st.text("Diabetes undiagnosed")

            #dislipedemiaPercentaje
            with CDislipidemia:
                if dislipidemiaPercentaje > 0:
                    dislipidemiaSourceText={"text": [getText(dislipidemiaPercentaje, diagnosed[1])]}
                    textString= dislipidemiaSourceText["text"][0]
                    nodislipidemiaPercentaje = 1-dislipidemiaPercentaje
                    dislipidemiaSource = {"category": ["dislipidemia", "nodislipidemia"], "value": [dislipidemiaPercentaje, nodislipidemiaPercentaje]}
                    dislipidemiaDataframe = pd.DataFrame(dislipidemiaSource) 
                    dislipidemiaTextDataframe= pd.DataFrame(dislipidemiaSourceText)
                    percentajePalete = getPercentajePalette(dislipidemiaPercentaje, textString)

                    dislipidemiaBase = alt.Chart(dislipidemiaDataframe).encode(
                        alt.Theta("value:Q").stack(True),
                        alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
                    )

                    dislipidemia_arc = dislipidemiaBase.mark_arc(
                        radius=80,
                        radius2=100
                    ).properties(title = alt.TitleParams("Dislipidemia", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

                    text = alt.Chart(dislipidemiaTextDataframe).mark_text(fontSize=25, color=getTextColor(textString), fontWeight="bold").encode(
                        text="text:N"
                    )

                    st.altair_chart(dislipidemia_arc + text, use_container_width=True)

                else:
                    st.text("dislipidemia undiagnosed")

            #obesityPercentaje
            with CObesity:
                if obesityPercentaje > 0:
                    obesitySourceText={"text": [getText(obesityPercentaje, diagnosed[2])]}
                    textString= obesitySourceText["text"][0]
                    noobesityPercentaje = 1-obesityPercentaje
                    obesitySource = {"category": ["obesity", "xnoobesity"], "value": [obesityPercentaje, noobesityPercentaje]}
                    obesityDataframe = pd.DataFrame(obesitySource) 
                    obesityTextDataframe= pd.DataFrame(obesitySourceText)
                    percentajePalete = getPercentajePalette(obesityPercentaje, textString)

                    obesityBase = alt.Chart(obesityDataframe).encode(
                        alt.Theta("value:Q").stack(True),
                        alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
                    )

                    obesity_arc = obesityBase.mark_arc(
                        radius=80,
                        radius2=100
                    ).properties(title = alt.TitleParams("obesity", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

                    text = alt.Chart(obesityTextDataframe).mark_text(fontSize=25, color=getTextColor(textString), fontWeight="bold").encode(
                        text="text:N"
                    )

                    st.altair_chart(obesity_arc + text, use_container_width=True)

                else:
                    st.text("obesity undiagnosed")
                
                
            st.html("<div style='position: absolute !important; top:-550px !important; '>")
            # nashPercentaje
            with CNash:
                if nashPercentaje > 0:
                    nashSourceText={"text": [getText(nashPercentaje, diagnosed[3])]}
                    textString= nashSourceText["text"][0]
                    nonashPercentaje = 1-nashPercentaje
                    nashSource = {"category": ["nash", "nonash"], "value": [nashPercentaje, nonashPercentaje]}
                    nashDataframe = pd.DataFrame(nashSource) 
                    nashTextDataframe= pd.DataFrame(nashSourceText)
                    percentajePalete = getPercentajePalette(nashPercentaje, textString)

                    nashBase = alt.Chart(nashDataframe).encode(
                        alt.Theta("value:Q").stack(True),
                        alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
                    )

                    nash_arc = nashBase.mark_arc(
                        radius=80,
                        radius2=100
                    ).properties(title = alt.TitleParams("Nash", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

                    text = alt.Chart(nashTextDataframe).mark_text(fontSize=25, color=getTextColor(textString), fontWeight="bold").encode(
                        text="text:N"
                    )

                    st.altair_chart(nash_arc + text, use_container_width=True)

                else:
                    st.text("nash undiagnosed")
            
            # kidneyDiseasePercentaje
            with CKidney:
                if kidneyDiseasePercentaje > 0:
                    kidneyDiseaseSourceText={"text": [getText(kidneyDiseasePercentaje, diagnosed[4])]}
                    textString= kidneyDiseaseSourceText["text"][0]
                    nokidneyDiseasePercentaje = 1-kidneyDiseasePercentaje
                    kidneyDiseaseSource = {"category": ["kidneyDisease", "nokidneyDisease"], "value": [kidneyDiseasePercentaje, nokidneyDiseasePercentaje]}
                    kidneyDiseaseDataframe = pd.DataFrame(kidneyDiseaseSource) 
                    kidneyDiseaseTextDataframe= pd.DataFrame(kidneyDiseaseSourceText)
                    percentajePalete = getPercentajePalette(kidneyDiseasePercentaje, textString)

                    kidneyDiseaseBase = alt.Chart(kidneyDiseaseDataframe).encode(
                        alt.Theta("value:Q").stack(True),
                        alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
                    )

                    kidneyDisease_arc = kidneyDiseaseBase.mark_arc(
                        radius=80,
                        radius2=100
                    ).properties(title = alt.TitleParams("KidneyDisease", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

                    text = alt.Chart(kidneyDiseaseTextDataframe).mark_text(fontSize=25, color=getTextColor(textString), fontWeight="bold").encode(
                        text="text:N"
                    )

                    st.altair_chart(kidneyDisease_arc + text, use_container_width=True)

                else:
                    st.text("kidneyDisease undiagnosed")

            # heartDiseasePercentaje
            with CHeart:
                if heartDiseasePercentaje > 0:
                    heartDiseaseSourceText={"text": [getText(heartDiseasePercentaje, diagnosed[5])]}
                    textString= heartDiseaseSourceText["text"][0]
                    noheartDiseasePercentaje = 1-heartDiseasePercentaje
                    heartDiseaseSource = {"category": ["HeartDisease", "noheartDisease"], "value": [heartDiseasePercentaje, noheartDiseasePercentaje]}
                    heartDiseaseDataframe = pd.DataFrame(heartDiseaseSource) 
                    heartDiseaseTextDataframe= pd.DataFrame(heartDiseaseSourceText)
                    percentajePalete = getPercentajePalette(heartDiseasePercentaje, textString)

                    heartDiseaseBase = alt.Chart(heartDiseaseDataframe).encode(
                        alt.Theta("value:Q").stack(True),
                        alt.Color("category:N", legend=None, scale=alt.Scale(range=percentajePalete))
                    )

                    heartDisease_arc = heartDiseaseBase.mark_arc(
                        radius=80,
                        radius2=100
                    ).properties(title = alt.TitleParams("heartDisease", anchor='middle', frame='bounds', dy= 70, fontWeight="bold"))

                    text = alt.Chart(heartDiseaseTextDataframe).mark_text(fontSize=25, color=getTextColor(textString), fontWeight="bold").encode(
                        text="text:N"
                    )

                    st.altair_chart(heartDisease_arc + text, use_container_width=True)

                else:
                    st.text("heartDisease undiagnosed")
                st.html("</div>")

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
                st.html("</br></br></br><p>Blood Pressure</p>")
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

