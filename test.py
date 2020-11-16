import requests
import re
import json
import cloudscraper
import math
import numpy
import time


# # Let's make a request and put the whole thing in a file
# reso  = requests.get("https://www.amazon.com/events/holidaydash/ref=gbps_ftr___wht_16579601?gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,sortOrder:BY_SCORE,enforcedCategories:165796011&ie=UTF8")


# with open("result.html",'w+') as f:
#     f.write(reso.text)



# Retrieving deals

#POST https://www.amazon.com/xa/dealcontent/v2/GetDeals?nocache=1605511494127

# We must parse this link perhaps from the main page result

# I highly suspect this link knows which deals you want to get by checking the "Referer" header

# Referer: https://www.amazon.com/events/holidaydash/ref=gbps_ftr___wht_16579601?gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,sortOrder:BY_SCORE,enforcedCategories:165796011&ie=UTF8&nocache=1605511176367

# It tells where you've been before, where were you when this request was made




TARGET_URL = "https://www.amazon.com/events/holidaydash/ref=gbps_ftr___wht_16579601?gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,sortOrder:BY_SCORE,enforcedCategories:165796011&ie=UTF8"


# The reason we want to use a "Session" is to keep cookies
sess = cloudscraper.CloudScraper(browser={
                            'browser': 'firefox',
                            'platform': 'windows',
                            'mobile': False
                        })
firstResponse = sess.get(TARGET_URL)

htmlMainPage = firstResponse.text
firstResponseHeaders = firstResponse.headers

with open('headers.txt', 'w+') as f:
    f.write(json.dumps(firstResponseHeaders.__dict__))

with open("result.html",'w+',encoding='utf-8') as f:
    f.write(htmlMainPage)



def grabSessionID(body):
    print('Grabbing SessionID')
    regx = "(?<=ue_sid = ').*(?=')"
    for match in re.findall(regx,body):
        return match

def grabMarketplaceID(body):
    print('Grabbing MarketplaceID')
    regx = "(?<=ue_mid = ').*(?=')"
    for match in re.findall(regx,body):
        return match




# Grab all deal IDs


def grabDealIds():
    dealsRegex = r"(?:\"sortedDealIDs\" : )\[.+?\]"
    foundResults = re.findall(dealsRegex,htmlMainPage,flags=re.MULTILINE | re.DOTALL)
    # Only return the first chunk
    if len(foundResults) < 1:
        exit("Could not find any deals")
    tmp =  foundResults[0]
    objStr = "{"+tmp+"}"
    arr = json.loads(objStr)['sortedDealIDs']
    ret = []
    for item in arr:
        ret.append(item)
    print ("Found " + str(len(ret)) + " deals")
    return ret










# When forging AJAX these are usually the most important headers
headers = {
    'X-Requested-With' :'XMLHttpRequest',
    'Origin': 'https://www.amazon.com',
    'Host': 'www.amazon.com',
    'Referer': TARGET_URL
}


targetDealIds = grabDealIds()

# We want to split it into chunks of 100 at most

equalChunksAmount = int(math.ceil(len(targetDealIds)/100))
dealsChunks = numpy.array_split(targetDealIds,equalChunksAmount)




def genAjaxReqPostData(d):
    dealTargets = []
    for dealId in d:
        dealTargets.append({"dealID": dealId})
    return {"requestMetadata":{"marketplaceID":grabMarketplaceID(htmlMainPage),"clientID":"goldbox_mobile_pc","sessionID":grabSessionID(htmlMainPage)},"dealTargets":dealTargets,"responseSize":"ALL","itemResponseSize":"DEFAULT_WITH_PREEMPTIVE_LEAKING","widgetContext":{"pageType":"Events","deviceType":"pc","refRID":"1R6S02Y0N4A394K01MZZ"},"customerContext":{"languageOfPreference":"en_US"}}

for chunk in dealsChunks:
    
    print ('Requesting data for ' + str(len(chunk)) + ' deals')
    postData = genAjaxReqPostData(chunk)
    curTimestamp = time.time()
    res = sess.post("https://www.amazon.com/xa/dealcontent/v2/GetDeals?nocache=1605511494127",headers=headers,json=postData)

    # Save response as JSON object
    
    with open(f'results-{curTimestamp}.json','w+',encoding='utf-8') as f:
        f.write(res.text)
