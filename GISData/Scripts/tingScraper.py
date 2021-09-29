from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from os.path import exists

class MasterAddressReader():
    def read(self):
        locations = []
        with open('../RawCSVs/Master_Address_Table.csv', 'r') as csvfile:
            csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in csvReader:
                streetNumber = row[2]
                unit = row[3]
                postal = row[9]

                # Concatenate all of the potential street parts if they exist into a single street address
                street = ""
                street = self.append(row[5], street)
                street = self.append(row[6], street)
                street = self.append(row[7], street)
                street = self.append(row[8], street)
                locations.append(Location("%s %s" % (streetNumber, street), postal, unit))
        print("Total of %s locations" % len(locations))
        return locations

    def append(self, check, to):
        if check and check != " " and check != "":
            to = "%s%s " % (to, check)
        return to


class Location():
    def __init__(self, address, postal, unit):
        self.address = address
        self.postal = postal
        self.unit = unit

    def equals(self, otherLocation):
        return self.address == otherLocation.address and self.postal == otherLocation.postal and self.unit == otherLocation.unit

    def description(self):
        return "%s %s %s" % (self.address, self.unit, self.postal)

    def print(self):
        print(self.description())

class TingBot():
  def __init__(self):
      self.driver = webdriver.Chrome("/usr/local/bin/chromedriver")

  def launchSite(self):
    #   seed output file if it doesn't exist, otherwise we'll be appending to existing structure
      filePath = "../RawCSVs/rawScraped.csv"
      if not exists(filePath):
          with open(filePath, 'w') as f:
              f.write("")
      else:
        #   If file exists look at the last line to determine where to pick up
          with open(filePath, 'r') as csvfile:
              csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
              rows = list(csvReader)
              self.rowCount = len(rows)
              print("%s cached from previous run" % self.rowCount)
              lastLine = rows[self.rowCount-1]
              address = lastLine[0]
              unit = lastLine[1]
              postal = lastLine[2]
              self.seedLocation = Location(address, postal, unit)
              print("Skipping to %s" % self.seedLocation.description())

      self.driver.get('https://ting.com/internet/town/charlottesville')
      element = WebDriverWait(self.driver, 5).until(
          EC.presence_of_element_located((By.ID, "addressCheckerField"))
      )
    #   Sleep a bit longer for initial load
      time.sleep(4)

  def checkLocations(self, locations):
      skip = False
      if self.seedLocation:
          skip = True
      for location in locations:
          if skip:
            #   print("Skipping %s" % location.description())
              if self.seedLocation.equals(location):
                  skip = False
              continue

          self.checkAddress(location.address, location.postal, location.unit)

  def checkAddress(self, address, postal, unit):
    addressField = self.driver.find_element_by_id("addressCheckerField")
    addressField.send_keys(address)
    
    unitField = self.driver.find_element_by_id("unit_number")
    unitField.send_keys(unit)

    postalCodeField = self.driver.find_element_by_id("postal_code")
    postalCodeField.send_keys(postal)

    time.sleep(1)
    postalCodeField.send_keys(Keys.ENTER)
    time.sleep(1)

    src = self.driver.page_source
    preorder = 'Pre-order now' in src
    available = 'Ting Internet is ready' in src or 'You are ready for Ting Internet' in src
    if preorder:
        state = "NOT AVAILABLE"
    elif available:
        state = "AVAILABLE"
    else:
        state = "UNKNOWN STATE"
    
    self.driver.back()
    # Don't have to wait as long after back button due to caching
    time.sleep(1)

    with open("../RawCSVs/rawScraped.csv", "a") as csvFile:
        self.rowCount += 1
        line = "%s,%s,%s,%s\n" %(address, unit, postal, state)
        csvFile.write(line)
        print("%s: -- %s" % (self.rowCount, line))

  def close(self):
      self.driver.close()


def processAddresses():
    # try:
        addressReader = MasterAddressReader()
        locations = addressReader.read()

        bot = TingBot()
        bot.launchSite()
        bot.checkLocations(locations)
        bot.close()
        return True
    # except:
    #     return False

succeeded = False
failedCount = -1
while not succeeded and failedCount < 1000:
    failedCount += 1
    succeeded = processAddresses()
    if not succeeded:
        rest = 15
        print("An error was thrown. Failed %s times so far. Letting site rest for %s seconds and then resetting bot..." % ((failedCount + 1), rest))
        time.sleep(rest)
print("Finished: Failed %s times" % failedCount)