import dml
import prov.model
import datetime
import uuid
import sys

class formatRouteCoords(dml.Algorithm):
    contributor = 'bkin18_cjoe_klovett_sbrz'
    reads = ['bkin18_cjoe_klovett_sbrz.emergency_routes']
    writes = ['bkin18_cjoe_klovett_sbrz.formatted_coords']

    @staticmethod
    def execute(trial=False):
        '''Formats coordinates to be used on the heatmap.'''
        startTime = datetime.datetime.now()
        
        print("Formatting route coordinates...            \n", end='\r')
        sys.stdout.write("\033[F") # Cursor up one line

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('bkin18_cjoe_klovett_sbrz', 'bkin18_cjoe_klovett_sbrz')
        db = client.repo

        modifiedDictionary = []
        fullCoordinateList = []
        
        for route_info in db['bkin18_cjoe_klovett_sbrz.route_coord_list'].find():
            coordinates = route_info['geometry']['coordinates']
            coordinateList = []

            for i in range(len(coordinates)):
                newCoordinate = {'lat': coordinates[i][1], 'lng': coordinates[i][0]}
                coordinateList.append(newCoordinate)

            fullCoordinateList.append(coordinateList)

        modifiedPiece = {'coordinates': fullCoordinateList}

        modifiedDictionary.append(modifiedPiece)

        repo.dropCollection('bkin18_cjoe_klovett_sbrz.formatted_coords')
        repo.createCollection('bkin18_cjoe_klovett_sbrz.formatted_coords')
        repo['bkin18_cjoe_klovett_sbrz.formatted_coords'].insert_many(modifiedDictionary)
  
        repo.logout()
        
        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('bkin18_cjoe_klovett_sbrz', 'bkin18_cjoe_klovett_sbrz')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#DataSet')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        ## Agent
        this_script = doc.agent('alg:bkin18_cjoe_klovett_sbrz#obtain_route_coords',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        ## Activity
        this_run = doc.activity('log:a'+str(uuid.uuid4()), startTime, endTime,
            { prov.model.PROV_TYPE:'ont:Retrieval', 'ont:Query':'.find()'})

        ## Entities
        route_coord_list = doc.entity('dat:bkin18_cjoe_klovett_sbrz.route_coord_list',
            { prov.model.PROV_LABEL:'Route Coordinate List', prov.model.PROV_TYPE:'ont:DataSet'})

        output = doc.entity('dat:bkin18_cjoe_klovett_sbrz.formatted_coords',
            { prov.model.PROV_LABEL:'Formatted Coordinates', prov.model.PROV_TYPE:'ont:DataSet'})


        doc.wasAssociatedWith(this_run , this_script)
        doc.used(this_run, route_coord_list, startTime)

        doc.wasAttributedTo(output, this_script)

        doc.wasGeneratedBy(output, this_run, endTime)

        doc.wasDerivedFrom(output, route_coord_list, this_run, this_run, this_run)

        repo.logout()

        return doc