import requests
import re
import json
import cloudscraper
import math
import numpy
import time
import socket
from urllib.parse import quote
from datetime import datetime
import os
from config import *

# current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
# new_folder = 'output_' + current_time
# os.mkdir(new_folder)

proxy_host = "proxy.crawlera.com"
proxy_port = "8010"
proxy_auth = crawlera_key  # Make sure to include ':' at the end
proxies = {"https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
           "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}


print ("Retrieving your public IP address...")
IP_ADDRESS = requests.get('https://api.ipify.org',proxies=proxies,verify="/home/krikagan1/code_folder/crawlera-ca.crt").text
print (IP_ADDRESS)



# The reason we want to use a "Session" is to keep cookies
sess = cloudscraper.CloudScraper(browser={
                            'browser': 'firefox',
                            'platform': 'windows',
                            'mobile': False
                        })


DEAL_STATES = ["AVAILABLE","EXPIRED","SOLDOUT","WAITLIST","WAITLISTFULL"]

USE_CATEGORY_COMBO = False



def run(categoryIds, dealStates):
    print(categoryIds)
    TARGET_URL = "https://www.amazon.com/events/holidaydash/ref=gbps_ftr___page_1?_encoding=UTF8&%2AVersion%2A=1&%2Aentries%2A=0&gb_f_GB-SUPPLE=enforcedCategories:{},dealStates:{},page:11,sortOrder:BY_SCORE,dealsPerPage:48&ie=UTF8".format(quote(quote(','.join(categoryIds))),quote(quote(','.join(DEAL_STATES))))

    print(TARGET_URL)
    firstResponse = sess.get(TARGET_URL,proxies=proxies,verify="/home/krikagan1/code_folder/crawlera-ca.crt")

    htmlMainPage = firstResponse.text
    firstResponseHeaders = firstResponse.headers

    with open(new_folder+"/headers.txt", 'w+') as f:
        f.write(json.dumps(firstResponseHeaders.__dict__))

    with open(new_folder+"/result.html",'w+',encoding='utf-8') as f:
        f.write(htmlMainPage)



    def grabSessionID(body):
        regx = "(?<=ue_sid = ').*(?=')"
        for match in re.findall(regx,body):
            return match

    def grabMarketplaceID(body):
        regx = "(?<=ue_mid = ').*(?=')"
        for match in re.findall(regx,body):
            return match

    def grabTotalDeals(body):
        regx = '(?<="selectedDealsCount" : )[0-9]+?(?=,)'
        for match in re.findall(regx,body):
            return int(match)

    def noCache():
        return str(time.time()).replace(".","")

    MARKETPLACE_ID = grabMarketplaceID(htmlMainPage)
    SESSION_ID = grabSessionID(htmlMainPage)
    TOTAL_DEALS = grabTotalDeals(htmlMainPage)

    print('MARKETPLACE_ID = '+str(MARKETPLACE_ID))
    print('SESSION_ID = '+str(SESSION_ID))
    print('TOTAL_DEALS = '+str(TOTAL_DEALS))


    # # When forging AJAX these are usually the most important headers
    headers = {
        'X-Requested-With' :'XMLHttpRequest',
        'Origin': 'https://www.amazon.com',
        'Host': 'www.amazon.com',
        'Referer': TARGET_URL
    }


    def grabAllDealsIds(cats,deals):
        grabbedDealsArrayOfIds = []
        grabbedDealsCnt = TOTAL_DEALS
        curPage = 0
        while grabbedDealsCnt > 0:
            grabbedDealsCnt-=300
            curPage+=1
            postData = {"requestMetadata":{"clientID":"goldbox_mobile_pc","marketplaceID":MARKETPLACE_ID,"sessionID":SESSION_ID},"queryProfile":{"dealStates":deals,"includedCategories":cats,"excludedExtendedFilters":{"MARKETING_ID":["TFSRestricted3P","bfexclude","excludegrid","fbaspringclearance2018","huntingrestrict","restrictedcontent","tobykill","usoutlet"]}},"sortOrder":"BY_CUSTOM_CRITERION","version":"V2.2","page":curPage,"dealsPerPage":300,"widgetContext":{"pageType":"Events","deviceType":"pc","refRID":"19W37WAGKZ5NS2PP3H4J"},"customRequestAttributes":{"__type":"SponsoredDealsRequestAttributes:http://internal.amazon.com/coral/com.amazon.dcs.model.v2/","populateSponsoredDealAttributes":True,"interestBasedAdsOptOut":False,"widgetName":"sp_gb_main_supple","ipAddress":IP_ADDRESS,"experimentName":"casterly","experiments":{"DEALS_RANKING_EXPERIMENT":"T1"}}}
            noCacheVal = noCache()
            res = sess.post(f"https://www.amazon.com/xa/dealcontent/v2/GetDealMetadata?nocache={noCacheVal}",headers=headers,json=postData)
            try:
                resJs = json.loads(res.text)
                for dealId in resJs['sortedDealIDs']:
                    grabbedDealsArrayOfIds.append(dealId)
            except:
                pass
        return grabbedDealsArrayOfIds



    # We now grab all the deal ids of this scraping session
    allDealIds = grabAllDealsIds(categoryIds,dealStates)


    # print('allDealIds',allDealIds)


    # # We want to split it into chunks of 100 at most and get the details of each dealId

    equalChunksAmount = int(math.ceil(len(allDealIds)/100))
    dealsChunks = numpy.array_split(allDealIds,equalChunksAmount)


    def genAjaxReqPostData(d):
        dealTargets = []
        for dealId in d:
            dealTargets.append({"dealID": dealId})
        return {"requestMetadata":{"marketplaceID":grabMarketplaceID(htmlMainPage),"clientID":"goldbox_mobile_pc","sessionID":grabSessionID(htmlMainPage)},"dealTargets":dealTargets,"responseSize":"ALL","itemResponseSize":"DEFAULT_WITH_PREEMPTIVE_LEAKING","widgetContext":{"pageType":"Events","deviceType":"pc","refRID":"1R6S02Y0N4A394K01MZZ"},"customerContext":{"languageOfPreference":"en_US"}}

    for chunk in dealsChunks:

        print ('Requesting data for ' + str(len(chunk)) + ' deals')
        postData = genAjaxReqPostData(chunk)
        curTimestamp = str(round(time.time()))
        res = sess.post("https://www.amazon.com/xa/dealcontent/v2/GetDeals?nocache=1605511494127",headers=headers,json=postData)

        # Save response as JSON object

        new_file = "results_"+str(categoryId)+"_"+curTimestamp+".json"
        with open(new_folder+"/"+new_file,'w+',encoding='utf-8') as f:
            f.write(res.text)


if USE_CATEGORY_COMBO:
    run(CATEGORY_IDS,DEAL_STATES)
else:
    for categoryId in CATEGORY_IDS:
        try:
            run([categoryId],DEAL_STATES)
        except:
            continue
