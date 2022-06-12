# =============================================================================
#  USGS/EROS Inventory Service Example
#  Python - JSON API
#
#  Script Last Modified: 6/17/2020
#  Note: This example does not include any error handling!
#        Any request can throw an error, which can be found in the errorCode proprty of
#        the response (errorCode, errorMessage, and data properies are included in all responses).
#        These types of checks could be done by writing a wrapper similiar to the sendRequest function below
#  Usage: python download_data.py -u username -p password
# =============================================================================

import json
import requests
import sys
import time
from usgs import api
import argparse

username = 'n.zaycev'
password = '##Jf2ccu-5Y_B,,'
datasetName = "landsat_ot_c2_l2"

# send http request
def sendRequest(url, data, apiKey=None):
    json_data = json.dumps(data)
    print('apiKey', apiKey)
    if apiKey == None:
        response = requests.post(url, json_data)
    else:
        headers = {'X-Auth-Token': apiKey,
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
        response = requests.post(url, json_data, headers=headers)

    try:
        httpStatusCode = response.status_code
        if response == None:
            print("No output from service")
            sys.exit()
        output = json.loads(response.text)
        if output['errorCode'] != None:
            print(output['errorCode'], "- ", output['errorMessage'])
            sys.exit()
        if httpStatusCode == 404:
            print("404 Not Found")
            sys.exit()
        elif httpStatusCode == 401:
            print("401 Unauthorized")
            sys.exit()
        elif httpStatusCode == 400:
            print("Error Code", httpStatusCode)
            sys.exit()
    except Exception as e:
        response.close()
        print(e)
        sys.exit()
    response.close()

    return output['data']

def checkScenes():
    # try:
    api.logout()
    # except:
        # pass
    apiKey = api.login(username, password)
    scenes = api.scene_search(datasetName,
                              api_key=apiKey,
                              max_results=1,
                              where={
                                  "filterType": "and",
                                  "childFilters": [
                                      {
                                          "filterType": "value",
                                          "filterId": '61b0ca3aec6387e5',
                                          "value": '8',
                                          "operand": "="
                                      },
                                      {
                                          "filterType": "value",
                                          "filterId": "5f6a6fb2137a3c00",
                                          "value": 'T1',
                                          "operand": "="
                                      },
                                      {
                                          "filterType": "value",
                                          "filterId": "5e83d14f567d0086",
                                          "value": 'SP',
                                          "operand": "="
                                      }
                                  ]
                              })
    api.logout()
    return scenes

def searchScenes(startDate, endDate, spatial):
    # NOTE :: Passing credentials over a command line arguement is not considered secure
    #        and is used only for the purpose of being example - credential parameters
    #        should be gathered in a more secure way for production usage
    # Define the command line arguements
    print("\nRunning Scripts...\n")
    try:
        api.logout()
    except:
        pass
    apiKey = api.login(username, password)

    print("API Key: " + apiKey + "\n")

    print("Searching scenes...\n\n")

    lat, lng = None, None
    if spatial:
        lat = spatial['lat']
        lng = spatial['lng']

    scenes = api.scene_search(datasetName,
                              api_key=apiKey,
                              # max_results=10,
                              lat=lat,
                              lng=lng,
                              start_date=startDate,
                              end_date=endDate,
                              where={
                                  "filterType": "and",
                                  "childFilters": [
                                      {
                                          "filterType": "value",
                                          "filterId": '61b0ca3aec6387e5',
                                          "value": '8',
                                          "operand": "="
                                      },
                                      {
                                          "filterType": "value",
                                          "filterId": "5f6a6fb2137a3c00",
                                          "value": 'T1',
                                          "operand": "="
                                      },
                                      {
                                          "filterType": "value",
                                          "filterId": "5e83d14f567d0086",
                                          "value": 'SP',
                                          "operand": "="
                                      }
                                  ]
                              })
    api.logout()
    return scenes


def downloadScene(entityId):
    try:
        api.logout()
    except:
        pass

    apiKey = api.login(username, password)
    sceneIds = [entityId]
    downloadOptions = api.download_options(datasetName, sceneIds, api_key=apiKey)

    # Aggregate a list of available products
    requiredLayers = ['ST_TRAD', 'ST_ATRAN', 'ST_URAD', 'ST_DRAD', 'SR_B5', 'SR_B4', 'QA_PIXEL']
    # requiredLayers = ['QA_PIXEL']
    def check_name(name):
        for i in requiredLayers:
            if name.find(i) != -1 and name.find('.TIF') != -1:
                return True
        return False
    downloads = []
    for product in downloadOptions:
        # Make sure the product is available for this scene
        if product['available'] == True:
            # downloads.append({'entityId': product['entityId'],
            #                           'productId': product['id']})
            for file in product['secondaryDownloads']:
                if file['available'] == True and check_name(file['displayId']):
                    downloads.append({'entityId': file['entityId'],
                                      'productId': file['id']})
            break
    # return {'options': downloadOptions}
    # return {'dd': downloads}
    # Did we find products?
    if downloads:
        requestedDownloadsCount = len(downloads)
        # set a label for the download request
        label = "download-sample"
        # payload = {'downloads': downloads,
        #            'label': label}
        # Call the download to get the direct download urls
        requestResults = api.download_request(dataset=datasetName, downloads=downloads, label='test', api_key=apiKey)
        print('rr', requestResults)
        # PreparingDownloads has a valid link that can be used but data may not be immediately available
        # Call the download-retrieve method to get download that is available for immediate download
        if requestResults['preparingDownloads'] != None and len(requestResults['preparingDownloads']) > 0:
            payload = {'label': label}
            moreDownloadUrls = api.download_retrieve(label, apiKey)
            print('mdurls', moreDownloadUrls)

            downloadIds = []

            for download in moreDownloadUrls['available']:
                downloadIds.append(download['downloadId'])
                print("DOWNLOAD: " + download['url'])

            for download in moreDownloadUrls['requested']:
                downloadIds.append(download['downloadId'])
                print("DOWNLOAD: " + download['url'])

            # Didn't get all of the reuested downloads, call the download-retrieve method again probably after 30 seconds
            while len(downloadIds) < requestedDownloadsCount:
                preparingDownloads = requestedDownloadsCount - len(downloadIds)
                print("\n", preparingDownloads, "downloads are not available. Waiting for 30 seconds.\n")
                time.sleep(30)
                print("Trying to retrieve data\n")
                moreDownloadUrls = api.download_retrieve("test", apiKey)
                for download in moreDownloadUrls['available']:
                    if download['downloadId'] not in downloadIds:
                        downloadIds.append(download['downloadId'])
                        print("DOWNLOAD: " + download['url'])

        else:
            # Get all available downloads
            for download in requestResults['availableDownloads']:
                # TODO :: Implement a downloading routine
                print("DOWNLOAD: " + download['url'])
        print("\nAll downloads are available to download.\n")
        api.logout()
        return requestResults

    api.logout()
    return {}
