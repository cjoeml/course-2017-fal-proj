from flask import Flask, render_template, request
from pymongo import MongoClient # Database connector
import urllib.parse
import json
from sklearn.cluster import KMeans
import sys
import math
import numpy as np
import z3_routes_interactive
import pdb
import dml

app = Flask(__name__)

username = urllib.parse.quote_plus('bkin18_cjoe_klovett_sbrz')
password = urllib.parse.quote_plus('bkin18_cjoe_klovett_sbrz')
client = MongoClient('localhost', 27017, username=username, password=password, authSource="repo")    #Configure the connection to the database
db = client['repo'] #Select the database

roads = [x for x in db['bkin18_cjoe_klovett_sbrz.emergency_routes_dict'].find()][0]

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/visualization')
def visualization():
    # here we want to get the value of user (i.e. ?means=some-value)
    try:
        routes = int(request.args.get('routes'))
        means = int(request.args.get('means'))
    except ValueError:
        return "Please enter a valid integer input"

    if routes > 0 and means > 0:

        '''
        Generates kmeans data to be used in visualization
        '''
        building_list = []

        for building in db['bkin18_cjoe_klovett_sbrz.property_assessment_impBuilds'].find():
            if building['LATITUDE'] == '#N/A' or building['LONGITUDE'] == '#N/A':
                pass
            else:
                building_list.append( [float(building['LATITUDE']), float(building['LONGITUDE'])] )

        kmeans = KMeans(n_clusters=means)
        kmeans.fit(building_list)

        kmean_list = kmeans.cluster_centers_.tolist()
        closest_buildings_to_centroids = []

        for p1 in kmean_list:
            min_dist = sys.maxsize
    
            # Iterate through important buildings and find closest one (aka last_building)
            for building in db['bkin18_cjoe_klovett_sbrz.property_assessment_impBuilds'].find():
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

        '''
        Formats kmeans data to be used in visualization
        '''
        kMeansCoordinateList = []

        for kmeans_info in closest_buildings_to_centroids:
            coordinate_list = []
            centroid_coordinates = kmeans_info['NEARBY_CENTROID']
            nearest_building_info = kmeans_info['_id']
            nearest_building_coordinates = [{'lat': nearest_building_info['LATITUDE'], 'lng': nearest_building_info['LONGITUDE']}]
            coordinate_list.append(centroid_coordinates)
            coordinate_list.append(nearest_building_coordinates)
            kMeansCoordinateList.append(coordinate_list)

        kMeansData = [{'coordinates': kMeansCoordinateList}]



        print("You selected {} means and {} routes".format(means, routes))
        #streets = z3_routes_interactive.find_streets(routes) z3 is stupid
        #we = list(db['bkin18_cjoe_klovett_sbrz.formatted_coords'].find())
        #print(we)
        passTest = {'test': str(kMeansCoordinateList)}
        #passTest = kMeansDictionary
        #return render_template('heatmap.html', kMeansData=kMeansData)
        return render_template('heatmap.html', kMeansData=json.dumps(kMeansData))
    else:
        return "Please enter a valid number of means"


def routes():
    # here we want to get the value of user (i.e. ?means=some-value)
    routes = int(request.args.get('routes'))

if __name__ == "__main__":
    app.run()
