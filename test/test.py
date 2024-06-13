import pandas as pd
import altair as alt
import streamlit as st

df = pd.read_csv("./aaa.csv")
df = df[df["marital_status"]=="MARRIED"]
df = df[["subject_id", "admission_type"]]

col1, col2 = st.columns(2)

admisions = set(df["admission_type"].values)
subject_id = set(df["subject_id"].values)

admisionFilter = st.sidebar.selectbox("chosse the admission graf1", admisions)
admisionFilter2 = st.sidebar.selectbox("chosse the admission graf2", admisions)

palette = ["#f86","#21f","#9f6"]
graf1 = alt.Chart(df).transform_filter(alt.datum.admission_type==admisionFilter) .mark_bar().encode(
    x=alt.X("admission_type:N", axis=alt.Axis(labelAngle=-30)).sort("y"),
    y=alt.Y("subject_id:Q"),
    color = alt.Color("admission_type:N", scale=alt.Scale(range=palette))
).properties(title = "test graf1")

graf2 = alt.Chart(df).transform_filter(alt.datum.admission_type==admisionFilter2) .mark_bar().encode(
    x=alt.X("admission_type:N", axis=alt.Axis(labelAngle=-30)).sort("y"),
    y=alt.Y("subject_id:Q"),
    color = alt.Color("admission_type:N", scale=alt.Scale(range=palette))
).properties(title = "test graf2")


with col1:
    st.altair_chart(graf1, use_container_width=False)
with col2:
    st.altair_chart(graf2, use_container_width=False)
    st.html("<h1>Cosas!!!</h1>")



# import pandas as pd
# import altair as alt
# import streamlit as st
# import json

# df = pd.read_csv("./conjuntaRecortadaToCSV.csv")
# # Eliminar columnas que no se usaran
# df.drop(columns = ['id', 'ant', 'invoices'], inplace=True)

# # Se ordena por id
# # df = df.sort_values("_id", ascending=True)

# #obtenemos el total de pacientes
# totalCountPatients= df.shape[0]

# # creamos una copia para poder trabajar sin perder lo que hay en df y borramos de la copia lo que no necesitamos
# idEncounters= df.copy(deep=True) 
# idEncounters.drop(columns = ['gender', 'geoLocationInfo', 'sourceData', 'switchDate', 'year'], inplace = True) 

# # añandimos la columna con el recuento de encounters 
# def addencounterQuantityColumn(r):
#     r = r.replace("\"['PHYS']\"","\"PHYS\"").replace("'","\"")
#     return len(json.loads(r))
# idEncounters["encounter_quantity"] =idEncounters["encounters"].apply(lambda x:  addencounterQuantityColumn(x))

# # creamos una copia para poder borrar encounters
# idCountEncounters= idEncounters.copy(deep=True) 
# # idCountEncounters.drop(columns = ['encounters', "_id"], inplace = True) 
# idCountEncounters.drop(columns = ['encounters'], inplace = True) 

# # agrupamos por "encounter_quantity"
# encounterQuantityGroup = idCountEncounters.groupby(by=["encounter_quantity"]).count()

# print(encounterQuantityGroup)


# # #añadimos columna porcentaje
# # encounterQuantityGroup["encounter_percentaje"]= encounterQuantityGroup["_id"]*100/totalCountPatients
# # print(encounterQuantityGroup)

# # graf1 = alt.Chart(encounterQuantityGroup).mark_bar().encode(
# #     x=alt.X("encounter_quantity:N"),
# #     y=alt.Y("encounter_percentaje:N")
# # ).properties(title = "encounter-percentaje")

# # st.altair_chart(graf1, use_container_width=True)




# # print(encounterQuantityGroup["encounter_quantity"])
# # print(encounterQuantityGroup["encounter_percentaje"])

# # graf1 = alt.Chart(encounterQuantityGroup).mark_bar().encode(
# #     x='encounter_quantity',
# #     y='encounter_percentaje'
# # ).properties(title = "encounter-percentaje")

# # st.altair_chart(graf1, use_container_width=True)



# #encounterQuantityFilter = st.sidebar.selectbox("chosse by en", ids)


# # def convert(r):
# #     try:
# #         r = r.replace("\"['PHYS']\"","\"PHYS\"").replace("'","\"")
# #         return len(json.loads(r))
# #     except Exception as error:
# #         print("****************************ERROR****************************")
# #         print(r)
# #         print(error)
# #         print("*************************************************************")
    

# # df["encounter_quantity"] =df["encounters"].apply(lambda x:  convert(x))


# # ids = set(df["_id"].values)


# # idsPatientFilter = st.sidebar.selectbox("chosse patient by id", ids)

# # col1, col2 = st.columns(2)

# # graf1 = alt.Chart(df).transform_filter(alt.datum._id==idsPatientFilter).mark_bar().encode(
# #     x=alt.X("_id:N", axis=alt.Axis(labelAngle=-30)).sort("y"),
# #     y=alt.Y("encounter_quantity:Q"),
# # ).properties(title = "test patients")

# # palette = ["#f86","#21f"]
# # graf2 = alt.Chart(df).mark_bar().encode(
# #     x=alt.X("_id:N", axis=alt.Axis(labelAngle=-30)).sort("y"),
# #     y=alt.Y("encounter_quantity:Q"),
# #     color = alt.Color("_id:N", scale=alt.Scale(range=palette))
# # ).properties(title = "test patients")

# # with col1:
# #     st.altair_chart(graf1, use_container_width=True)
# # with col2:
# #     st.altair_chart(graf2, use_container_width=True)