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
        self.parcelStates = {}
        with open('../rawCSVs/addressesMappedToParcelGPID.csv', 'r') as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',', quotechar='|')
            # 0 - 108 W SOUTH ST ,
            # 1 - 201,
            # 2 - 22902,
            # 3 - UNKNOWN STATE
            # 4 - Parcel
            for row in csvReader:
                self.parcelStates[row[4]] = row[3]
    
    def processFile(self):
        lines = []
        with open('../GeoJSON/Parcel_Boundary_Area.geojson', 'r') as geoJson:
            for line in geoJson:
                if 'GPIN' in line:
                    # Add state
                    gpinIndex = line.index('GPIN')
                    objectIdIndex = line.index(', "OBJECTID"')
                    gpin = line[gpinIndex + 7:objectIdIndex]
                    if gpin in self.parcelStates.keys():
                        state = self.parcelStates[gpin]
                    else:
                        state = ""
                    lines.append(line.replace('"GPIN"', '"AVAILABLE_STATE": "%s", "GPIN"' % state))
                else:
                    lines.append(line)
        
        with open('../GeoJSON/Parcel_Boundary_Area_With_AvailabilityStates.geojson', 'w') as geoJson:
            for line in lines:
                geoJson.write(line)

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