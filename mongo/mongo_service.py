class MongoService():

    collection:any

    def __init__(self, mongoCollection):
        self.collection = mongoCollection
    
    def findById(self, id)->dict:
        res = self.collection.find_one({ "_id": id})
        return res
    
    def getquery(self, patientRegex, skip, limit, nationality, source, minYear,  maxYear, gender):
        query=[]

        queryMatch = {"$match":{}}
        queryMatch["$match"]["year"]= {
            "$gte":maxYear,
            "$lt":minYear
        }

        if nationality != "All":
            queryMatch["$match"]["geoLocationInfo.nationality"]= nationality

        if source != "All":
            queryMatch["$match"]["sourceData"]= source
        
        if gender != "All":
            queryMatch["$match"]["gender"]= gender
        
        if patientRegex != "":
            queryMatch["$match"]["_id"] = {"$regex":patientRegex}
        query.append(queryMatch)
        
        if limit > 0:
            query.append({ "$limit": skip + limit })
        if skip >= 0:
            query.append({ "$skip": skip })
        query.append({ "$sort" : { "_id" : 1 }})
        
        return query
    
    def getPatients(self, patientRegex, skip, limit, nationality, source, minYear,  maxYear, gender):
        res= self. collection.aggregate(self.getquery(patientRegex, skip, limit, nationality, source, minYear,  maxYear, gender))
        resList = list(res)
        patientList = []
        for patient in resList:
            patientList.append(patient["_id"])
        return patientList
    
    def getTotalLists(self,patientRegex, skip, limit, nationality, source, minYear,  maxYear, gender):
        query = self.getquery(patientRegex, skip, limit, nationality, source, minYear,  maxYear, gender)
        query.append({ "$project": { "geoLocationInfo.nationality": 1, "sourceData":1}})
        res = self.collection.aggregate(query)
        resList = list(res)
        return resList
    
    def getPipeLineStatus(self):

        res = self.collection.aggregate([{"$match":{"_id":"reporting"}},{ "$project": { "total_patients": 1, "nationality":1, "sources":1 }} ])
        return list(res)
    
    def updatePipeline(self, total, nationality, sources):
        self.collection.update_one({"_id":"reporting"},{'$set' :{"total_patients":total, "nationality":nationality, "sources":sources}}, True)
        
    

