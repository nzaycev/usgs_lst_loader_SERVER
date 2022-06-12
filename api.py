# from usgs import api
#
#
# def submit_where_query():
#
#     # USGS uses numerical codes to identify queryable fields
#     # To see which fields are queryable for a specific dataset,
#     # send off a request to dataset-fields
#
#     results = api.s()
#
#     for field in results['data']:
#         print(field)
#
#     # WRS Path happens to have the field id 20514
#     where = {
#         20514: '043'
#     }
#     results = api.search('LANDSAT_8_C1', 'EE', where=where, start_date='2017-04-01', end_date='2017-05-01', max_results=10, extended=True)
#
#     for scene in results['data']['results']:
#         print(scene)
#
# submit_where_query()

import json
from usgs import api

# Set the EarthExplorer catalog
node = 'EE'

# Set the Hyperion and Landsat 8 dataset
hyperion_dataset = 'EO1_HYP_PUB'
landsat8_dataset = 'LANDSAT_8'

# Set the scene ids
hyperion_scene_id = 'EO1H1820422014302110K2_SG1_01'
landsat8_scene_id = 'LC80290462015135LGN00'
api.logout()
session = api.login('n.zaycev', '##Jf2ccu-5Y_B,,')

print(session)
api_key = session['data']

# filters = api.dataset_filters('landsat_ot_c2_l2', api_key=api_key)
# # print("filters", json.dumps(filters))
# # print(json.dump(filters, open('t.json', 'w')))
scenes = api.scene_search('landsat_ot_c2_l2', api_key=api_key, max_results=10, where={
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

print(json.dumps(scenes))
# for scene in scenes['data']['results']:
#     print(scene)

# md = api.scene_metadata('landsat_ot_c2_l2', 'LC80990142022069LGN00', api_key)
# # do = api.download_request('landsat_ot_c2_l2', 'LC80990142022069LGN00', product_id='STANDARD', api_key=api_key)
# do = api.dataset_download_options('landsat_ot_c2_l2', api_key=api_key)
d = api.download_request('landsat_ot_c2_l2', entity_id='LC80100482022085LGN00', product_id="5e83d14fec7cae84", api_key=api_key)
# print('metadata', json.dumps(md))
print('download options', json.dumps(d))

dd = api.download_options('landsat_ot_c2_l2', ['LC80100102022085LGN00'], api_key=api_key)
downloads = []
dr = api.download_retrieve(downloads, api_key)
print('ddd', json.dumps(dd))
print('ddr', json.dumps(dr))