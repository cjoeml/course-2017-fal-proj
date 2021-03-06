import dml
import prov.model
import datetime
import uuid
from sklearn.cluster import KMeans
import sys
import math
import numpy as np

class find_buildings_and_centroids(dml.Algorithm):
    contributor = 'bkin18_cjoe_klovett_sbrz'
    reads = ['bkin18_cjoe_klovett_sbrz.property_assessment_impBuilds']
    writes = ['bkin18_cjoe_klovett_sbrz.closest_buildings_to_centroids']

    @staticmethod
    def dist(p1, p2):
        # Standard distance formula #
        return math.sqrt( (p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 )

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        print("Finding closest buildings...       \n", end='\r')
        sys.stdout.write("\033[F") # Cursor up one line

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('bkin18_cjoe_klovett_sbrz', 'bkin18_cjoe_klovett_sbrz')
        db = client.repo
        collection = db['bkin18_cjoe_klovett_sbrz.property_assessment_impBuilds']

        # This is a constant that we can change if we want to
        K = 9

        # Set up the lat and long coordinates
        building_list = []
        for building in collection.find():
            if building['LATITUDE'] == '#N/A' or building['LONGITUDE'] == '#N/A':
                pass
            else:
                building_list.append( [float(building['LATITUDE']), float(building['LONGITUDE'])] )

        # Build kmeans
        kmeans = KMeans(n_clusters=K)
        kmeans.fit(building_list)
        
        # Build the input list (kmean_list) and the output list (closest_buildings_to_centroids)
        kmean_list = kmeans.cluster_centers_.tolist()
        closest_buildings_to_centroids = []


        # This is kind of repetitive we can probably try and find a better solution
        for p1 in kmean_list:
            min_dist = sys.maxsize
    
            # Iterate through important buildings and find closest one (aka last_building)
            for building in collection.find():
                if building['LATITUDE'] == '#N/A' or building['LONGITUDE'] == '#N/A':
                    pass
                else:
                    p2 = ( float(building['LATITUDE']), float(building['LONGITUDE']) )
                    distance = math.sqrt( (p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 )
                    if distance < min_dist:
                        min_dist = distance
                        last_building = building

            # Rebuild buildings to include its ID and the centroids it is closest to

            this_building = {}
            this_building['_id'] = last_building
            this_building['NEARBY_CENTROID'] = p1
            this_building["DIST_TO_CENTROID"] = min_dist
            
            closest_buildings_to_centroids.append(this_building)

        repo.dropCollection('bkin18_cjoe_klovett_sbrz.closest_buildings')
        repo.dropCollection('bkin18_cjoe_klovett_sbrz.closest_buildings_to_centroid')
        repo.dropCollection('bkin18_cjoe_klovett_sbrz.closest_buildings_to_centroids')
        repo.createCollection('bkin18_cjoe_klovett_sbrz.closest_buildings_to_centroids')
        
        repo['bkin18_cjoe_klovett_sbrz.closest_buildings_to_centroids'].insert_many(closest_buildings_to_centroids)

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
        this_script = doc.agent('alg:bkin18_cjoe_klovett_sbrz#find_buildings_and_centroids',
            { prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        
        ## Activity
        this_run = doc.activity('log:a'+str(uuid.uuid4()), startTime, endTime, 
            { prov.model.PROV_TYPE:'ont:Retrieval', 'ont:Query':'.find()'})

        ## Entity
#        resource = doc.entity('bdp:38173410110330', {'prov:label': 'Buildings and Centroids', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'json'})
        imp_b_input = doc.entity('dat:bkin18_cjoe_klovett_sbrz#property_assessment_impBuilds',
            {'prov:label': 'Important Buildings', prov.model.PROV_TYPE: 'ont:DataSet'})
        output = doc.entity('dat:bkin18_cjoe_klovett_sbrz#buildings_and_centroids',
            {'prov:label': 'Buildings and Centroids Data', prov.model.PROV_TYPE: 'ont:DataSet'})

        doc.wasAssociatedWith(this_run, this_script)
        doc.used(this_run, imp_b_input, startTime)

        doc.wasAttributedTo(output, this_script)
        doc.wasGeneratedBy(output, this_run, endTime)
        doc.wasDerivedFrom(output, imp_b_input, this_run, this_run)

        repo.logout()

        return doc
