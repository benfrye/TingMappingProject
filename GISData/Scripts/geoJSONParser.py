import csv
from os.path import exists

class address():
    def __init__(self, x, y, objectId, masterAddressId, number, predir, street, suffix, postdir, unit):
        self.objectId = objectId
        self.masterAddressId = masterAddressId
        self.number = number
        self.predir = predir
        self.street = street
        self.suffix = suffix
        self.postdir = postdir
        self.unit = unit
        self.x = x
        self.y = y

    def key(self):
        street = ""
        street = self.append(self.predir, street)
        street = self.append(self.street, street)
        street = self.append(self.suffix, street)
        street = self.append(self.postdir, street)
        return "%s %s" % (self.number, street)

    def append(self, check, to):
        if check and check != " " and check != "":
            to = "%s%s " % (to, check)
        return to

    def description(self):
        description = self.key()
        if hasattr(self, 'availableState'):
            return "%s - %s" % (description, self.availableState)
        else:
            return description
        

class outputProcesser():
    def loadFiles(self):
        self.masterAddresses = {}
        with open('../RawCSVs/Master_Address_Points.csv', 'r') as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',', quotechar='|')
            for row in csvReader:
                # 0 - X,
                # 1 - Y,
                # 2 - OBJECTID,
                # 3 - geo_MAT_Status,
                # 4 - geo_MAT_ST_NUMBER,
                # 5 - geo_MAT_PREDIR,
                # 6 - geo_MAT_ST_NAME,
                # 7 - geo_MAT_SUFFIX,
                # 8 - geo_MAT_POSTDIR,
                # 9 - centroid_BUILD_STREET,
                # 10 - unit,
                # 11 - address,
                # 12 - geo_MAT_MasterAddressID
                x = row[0]
                y = row[1]
                objectId = row[2]
                masterId = row[12]
                number = row[4]
                predir = row[5]
                street = row[6]
                suffix = row[7]
                postdir = row[8]
                unit = row[10]
                rowAddress = address(x, y, objectId, masterId, number, predir, street, suffix, postdir, unit)
                self.masterAddresses[rowAddress.key()] = rowAddress
        # for row in self.masterAddresses:
        #     print(row)
        
        self.scrapedAddresses = []
        with open('../RawCSVs/rawScraped.csv', 'r') as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',', quotechar='|')
            # 0 - 108 W SOUTH ST ,
            # 1 - 201,
            # 2 - 22902,
            # 3 - UNKNOWN STATE
            # 4 - Parcel
            for row in csvReader:
                street = row[0]
                if street in self.masterAddresses.keys():
                    state = row[3]
                    rowAddress = self.masterAddresses[street]
                    rowAddress.availableState = state
                    if len(row) > 4:
                        parcel = row[4]
                        rowAddress.parcelId = parcel
                    self.masterAddresses[street] = rowAddress

        # for row in self.masterAddresses.values():
        #     print(row.description())
    
    def processFile(self):
        header = '{\n"type": "FeatureCollection",\n"name": "%s",\n"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },\n"features": [\n'
        footer = ']\n}\n'

        availableHeader = header % 'Available_Points'
        availableFile = '/Users/fryeb/git/TingHouseMapping/available.geojson'
        availableRows = []
        for index, (key, row) in enumerate(self.masterAddresses.items()):
            if hasattr(row, 'availableState'):
                state = row.availableState
            else:
                state = ""
            
            if hasattr(row, 'parcelId'):
                parcelId = row.parcelId
            else:
                parcelId = ""
            processedRow = '{ "type": "Feature", "properties": { "PARCELID": "%s", "AVAILABLESTATE": "%s", "OBJECTID": %s, "geo_MAT_Status": null, "geo_MAT_ST_NUMBER": "%s", "geo_MAT_PREDIR": "%s", "geo_MAT_ST_NAME": "%s", "geo_MAT_SUFFIX": "%s", "geo_MAT_POSTDIR": "%s", "centroid_BUILD_STREET": "", "unit": "%s", "address": "", "geo_MAT_MasterAddressID": %s }, "geometry": { "type": "Point", "coordinates": [ %s, %s ] } },\n' % (parcelId, state, row.objectId, row.number, row.predir, row.street, row.suffix, row.postdir, row.unit, row.masterAddressId, row.x, row.y)
            availableRows.append(processedRow)

        self.buildGeoJSON(availableFile, availableHeader, self.cleanRows(availableRows), footer)

    def cleanRows(self, rows):
        rows[len(rows) - 1] = rows[len(rows) - 1].replace(',\n', '\n')
        return rows

    def buildGeoJSON(self, filename, header, rows, footer):
        with open(filename, 'w') as geoJSONFile:
            geoJSONFile.write(header)
            for row in rows:
                geoJSONFile.write(row)
            geoJSONFile.write(footer)

processor = outputProcesser()
processor.loadFiles()
processor.processFile()