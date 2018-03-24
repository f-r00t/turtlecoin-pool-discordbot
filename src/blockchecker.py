import requests
import operator
import pickle

warnings = {}

# Number of warnings which should result in an alert
warning_treshhold = 3

try:
    pickle_in = open("warnings.pickle","rb")
    email_addresses = pickle.load(pickle_in)
except:
    print("No stored warnings")


def get_faulty_nodes():
    faulty_nodes = {}

    # Get list of pools
    r = requests.get(url='https://raw.githubusercontent.com/turtlecoin/turtlecoin-pools-json/master/turtlecoin-pools.json')

    pools = []

    pool_stats = {}

    for pool in r.json():
        pool_name = pool
        pool_api = r.json()[pool]['url']
        api_command = pool_api + "stats"

        try:
             re = requests.get(url=api_command)
             pool_stats[pool] = re.json()['network']

        except:
             print("Cannot connect to " + pool)
             id = pool+'0'
             if id in warnings:
                 warnings[id] += 1
             else:
                 warnings[id] = 1
             if warnings[id] > warning_treshhold - 1:
                 del warnings[id]
                 faulty_nodes[pool] = {'height': 0, 'error': 'unresponsive'} 
             continue

    block_heights = {}
    for pool in pool_stats:
        height = pool_stats[pool]['height']
        if height not in block_heights:
            block_heights[height] = 1
        else:
            block_heights[height] += 1
    correct_height = sorted(block_heights.items(), key=operator.itemgetter(1))[-1][0]

    for pool in pool_stats:
        if ( correct_height - pool_stats[pool]['height'] ) > 5:
            print(pool + " is down")

            id = pool+str(pool_stats[pool]['height'])

            if id in warnings:
                warnings[id] += 1
            else:
                warnings[id] = 1
            if warnings[id] > warning_treshhold - 1:
                del warnings[id]
                faulty_nodes[pool] = {'height': pool_stats[pool]['height'], 'error': '5blocksbehind'}

    return faulty_nodes
