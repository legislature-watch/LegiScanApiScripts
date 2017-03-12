from urllib.request import urlopen
import json, os, sys, base64
from bs4 import BeautifulSoup
import magic

### PDFs ###
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO, BytesIO


api_key = "73c27751415db981ca54148626719e2e"
files = "/Users/kprichard/ext/LegiScanApiScripts/billText"

### Get list of all bills for a state, get the bills individually, write them to disk ###
def writeBills(api_key, files, state):
    uri="https://api.legiscan.com/?key=%(api_key)s&op=getMasterList&state=%(state)s" % locals()
    print("Get master list... "+uri)
    r = urlopen(uri).read().decode('utf-8')
    json_obj = json.loads(r)
    js = json_obj.get('masterlist')
    bill_id_list= []

    for item in js.values():
        try:
            bill_id_list.append(item.get('bill_id'))
        except KeyError:
            pass

    bills = getBills(bill_id_list, api_key, files)

    num = 1
    for bill in bills:

        #iterate to the bill key
        #get the doc_id to append to the API call
        try:
            bill_num = bill.get("bill").get("bill_number")
        except AttributeError:
            bill_num = "bill" + str(num)
        try:
            doc_id = bill.get("bill").get("texts")[0].get("doc_id")
        except AttributeError:
            pass

        #append the doc_id to the API call and convert results to unicode string
        uri = 'https://api.legiscan.com/?key='+api_key+'&op=getBillText&id=%(doc_id)s' % locals()
        print("Getting bill text... "+uri)
        searchId = urlopen(uri).read().decode()

        #create json object with API data
        resultsId = ""
        try:
            resultsId = json.loads(searchId)
        except:
            print(searchId)
            continue

        #iterate to the document object
        resultDoc = resultsId.get('text').get('doc')

        #decode the MIME 64 encoded text
        decodedResults = base64.b64decode(resultDoc)

        media_type = magic.from_buffer(decodedResults)

        if media_type.startswith('PDF document'):
            textData = pdfExtractor(decodedResults)
        elif media_type.startswith('HTML document'):
            textData = htmlExtractor(decodedResults)
        else:
            print("Unknown media type:", media_type, uri)
            continue

        writeOneBill(textData, files, state, bill_num, doc_id)
        num += 1

def writeOneBill(billText, files, state, bill_num, doc_id):
    # write each instance of htmlText to a unique file
    # YOU'LL NEED TO CHANGE THE BELOW PATH TO WHEREVER YOUR LEGISCANAPI
    # DIRECTORY IS LOCATED.

    out_path = files + "/"+state+"/" + str(bill_num) + "_" + str(doc_id) + ".txt"
    out_fp = open(out_path, "wb")
    print("Writing: "+ str(bill_num)+" "+out_path)
    out_fp.write(billText.encode("ascii", errors="ignore"))
    out_fp.close()

def getBills(bill_list, api_key, files):
    """use the list of ids to increment api billText"""
    complete_bill_list = []
    for i in bill_list:
        uri = "https://api.legiscan.com/?key="+api_key+"&op=getBill&id=%(i)s" % locals()
        print("getBills "+uri)
        billUrl = urlopen(uri).read().decode()
        json_obj = json.loads(billUrl)
        complete_bill_list.append(json_obj)

    return complete_bill_list

def htmlExtractor(htmlObj):
    # once decoded, the text is in an HTML string, use bs4 to parse it
    bsObj2 = BeautifulSoup(htmlObj, "html.parser")
    for p in bsObj2.find_all('p'):
        if p.string:
            p.string.replace_with(p.string.strip())
#     print('bsObj2.style', bsObj2.style)
#     print('bsObj2', bsObj2)
#     bsObj2.style.decompose()

    # strip white space, encode in ascii and remove non-printing characters
    return str(bsObj2.getText())

def pdfExtractor(pdfObject):

    rsrcmgr = PDFResourceManager()
    inpstr = BytesIO(pdfObject)
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)

    # fp = file(path, 'rb')
    process_pdf(rsrcmgr, device, inpstr)
    inpstr.close()
    device.close()

    str = retstr.getvalue()
    retstr.close()
    return str

if __name__ == "__main__":
	states = sys.argv[1:] if len(sys.argv) > 1 else ["CO"]
	### get state as first param ###
	for state in states:
		print("Scanning legiscan.com for legislature=",state)
		### ensure output folder exists ###
		os.makedirs(os.path.join(files, state), mode=0o777, exist_ok=True)

		writeBills(api_key, files, state)
