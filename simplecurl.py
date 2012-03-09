import pycurl
import StringIO
import simplejson

# Perform a curl request and return a json result
def json(request):
  curlReq = pycurl.Curl()
  curlReq.setopt(pycurl.URL, request.__str__())
  curlReq.setopt(pycurl.FOLLOWLOCATION, 1)
  curlReq.setopt(pycurl.MAXREDIRS, 5)
  result = StringIO.StringIO()
  curlReq.setopt(pycurl.WRITEFUNCTION, result.write)
  curlReq.perform()
  result = StringIO.StringIO(result.getvalue())
  result = simplejson.load(result)
  return result

