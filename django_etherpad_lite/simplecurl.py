# Usage
# -----
#
# This file is designed to be dropped into python programs that need to use a
# REST API or similar service. Usage is quite simple - once imported, you need
# only construct your query, and pass it as an argument to simplecurl's json
# function.
#
# For more information or comments, please write me@sfyn.net
#
# Licensing
# ---------
#
# Copyright 2011 Sofian Benaissa.
# 
# This file is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version. 
# 
# This file is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more 
# details. You can consult the license at http://www.gnu.org/licenses/

import pycurl
import StringIO
import simplejson

def json(request):
  """Perform a curl request and returns a json result, formatted as an array

  Keywork arguments:
  request -- a string representing a url and querystring

  """
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

