import csv
from os.path import exists

class parcel:
    def __init__(self, parcelNumber, streetNumber, streetName, unit, gpin):
        self.parcelNumber = parcelNumber
        self.streetNumber = streetNumber
        self.streetName = streetName
        self.unit = unit
        self.gpin = gpin

    def key(self):
        return "%s %s " % (self.streetNumber, self.streetName)

    def description(self):
        return "%s: %s %s %s - %s" % (self.parcelNumber, self.streetNumber, self.streetAddress, self.unit, self.gpin)

class address:
    def __init__(self, streetAddress, unit, zip, availableState, parcelNumber):
        self.streetAddress = streetAddress
        self.unit = unit
        self.zip = zip
        self.availableState = availableState
        self.parcelNumber = parcelNumber
    
    def description(self):
        return "%s: %s %s %s - %s" % (self.parcelNumber, self.streetAddress, self.unit, self.zip, self.availableState)

class outputProcesser():
    def loadFiles(self):
        self.masterParcels = {}
        with open('../RawCSVs/Real_Estate_(Base_Data).csv', 'r') as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',', quotechar='|')
            # 0 - RecordID_Int,
            # 1 - ParcelNumber,
            # 2 - StreetNumber,
            # 3 - StreetName,
            # 4 - Unit,
            # 5 - StateCode,
            # 6 - TaxType,
            # 7 - Zone,
            # 8 - TaxDist,
            # 9 - Legal,
            # 10 - Acreage,
            # 11 - GPIN
            for row in csvReader:
                parcelNumber = row[1]
                streetNumber = row[2]
                streetName = row[3]
                unit = row[4]
                gpin = row[11]
                parsedParcel = parcel(parcelNumber, streetNumber, streetName, unit, gpin)
                self.masterParcels[parsedParcel.key()] = parsedParcel
        # for key in self.masterParcels.keys():
        #     print(key)
        
        self.scrapedAddresses = []
        with open('../RawCSVs/rawScraped.csv', 'r') as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',', quotechar='|')
            # 0 - 108 W SOUTH ST ,
            # 1 - 201,
            # 2 - 22902,
            # 3 - UNKNOWN STATE
            for row in csvReader:
                street = row[0]
                unit = row[1]
                zip = row[2]
                state = row[3]
                if street in self.masterParcels.keys():
                    parsedParcel = self.masterParcels[street].gpin
                else:
                    parsedParcel = ""
                self.scrapedAddresses.append(address(street, unit, zip, state, parsedParcel))
        
        # for row in self.scrapedAddresses:
        #     print(row.description())

    def parseFiles(self):
        with open('../RawCSVs/addressesMappedToParcelGPID.csv', 'w') as csvFile:
            # self.streetAddress = streetAddress
            # self.unit = unit
            # self.zip = zip
            # self.availableState = availableState
            # self.parcelNumber = parcelNumber
            for row in self.scrapedAddresses:
                csvFile.write("%s,%s,%s,%s,%s,\n" % (row.streetAddress, row.unit, row.zip, row.availableState, row.parcelNumber))

processor = outputProcesser()
processor.loadFiles()
processor.parseFiles()