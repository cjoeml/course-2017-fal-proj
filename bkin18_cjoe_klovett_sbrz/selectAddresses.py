import dml
import prov.model
import datetime
import uuid


class selectAddresses(dml.Algorithm):
    contributor = 'bkin18_cjoe_klovett_sbrz'
    reads = ['bkin18_cjoe_klovett_sbrz.property_assessment']
    writes = ['bkin18_cjoe_klovett_sbrz.property_assessment_addresses']

    @staticmethod
    def execute(trial=False):
        '''Select all of the addresses from the Property Assessment data set'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('bkin18_cjoe_klovett_sbrz', 'bkin18_cjoe_klovett_sbrz')

        db = client.repo
        collection = db['bkin18_cjoe_klovett_sbrz.property_assessment']
        x = []
        property_lookup = ['010', '019', '025', '026', '027', '111', '112', '113', '114', '115', '117', '118', '120',
                            '121', '122', '123', '124', '125', '126', '127', '128', '129', '300', '301']

        addresses = collection.find({}, {'ST_NAME': 1, 'PTYPE': 1})
        for address in addresses:
            if address['PTYPE'] in property_lookup:
                x.append(address)

        repo.dropCollection('bkin18_cjoe_klovett_sbrz.property_assessment_addresses')
        repo.createCollection('bkin18_cjoe_klovett_sbrz.property_assessment_addresses')
        repo['bkin18_cjoe_klovett_sbrz.property_assessment_addresses'].insert_many(x)
        repo['bkin18_cjoe_klovett_sbrz.property_assessment_addresses'].metadata({'complete': True})
        repo.dropCollection('bkin18_cjoe_klovett_sbrz.property_assessment')

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
        repo.authenticate('sbrz_nedg', 'sbrz_nedg')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#DataSet')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:sbrz_nedg#selectAddressesColleges',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        property_address_db = doc.entity('dat:sbrz_nedg#property_assessment',
            {'prov:label': 'property_assessment', prov.model.PROV_TYPE: 'ont:DataSet'})
        address_db = doc.entity('dat:sbrz_nedg#property_assessment_addresses',
                                {'prov:label': 'property_assessment_addresses', prov.model.PROV_TYPE: 'ont:DataSet'})
        select_address_data = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(select_address_data, this_script)
        doc.usage(property_address_db, address_db, startTime, None)

        doc.wasAttributedTo(this_script, this_script)
        doc.wasGeneratedBy(select_address_data)
        doc.wasDerivedFrom(property_address_db, address_db)

        repo.logout()

        return doc