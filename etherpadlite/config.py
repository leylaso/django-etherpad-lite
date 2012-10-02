"""
This file centralizes configuration of this module
"""

# This sets the number of seconds to keep the session cookie and server side
# session alive for an author's access to a pad. The default is one day

SESSION_LENGTH = 1 * 24 * 60 * 60

# Uncomment this tuple and supply values to define a testing server for the
# automated tests
#
# TESTING_SERVER = {
#   'title': 'Testing Server',
#   'url': 'http://example.com:9001',
#   'apikey': 'secret'
# }
