import cf_deployment_tracker
import argparse
import os
from app.app import app

cf_deployment_tracker.track()

# On Bluemix, get the port number from the environment variable VCAP_APP_PORT
# When running this app on the local machine, default the port to 8080

parser = argparse.ArgumentParser()

parser.add_argument("--debug",
                    '-d',
                    required=False,
                    help="True if you want to debug your app",
                    metavar='DEBUG',
                    default='True')
parser.add_argument("--host",
                    '-H',
                    required=False,
                    help="The host where you want to run your app",
                    metavar='HOST',
                    default='127.0.0.1')
parser.add_argument("--port",
                    '-p',
                    required=False,
                    help="The port where you want to serve your app",
                    metavar='PORT',
                    default='5000')
parser.add_argument("--threaded",
                    '-t',
                    required=False,
                    help="Only in developer mode",
                    metavar='THREADED',
                    default='False')

args = parser.parse_args()

if not ("VCAP_APP_HOST" in os.environ):
    app.config['HOST'] = str(args.host)
    app.config['PORT'] = int(args.port)
    app.config['DEBUG'] = False if args.debug == 'False' else True
    app.config['THREADED'] = False if args.threaded == 'False' else True

# def main(argv):
#     try:
#         opts, args = getopt.getopt(argv,"hd:p:H:",["debug=","port=","host="])
#     except getopt.GetoptError:
#         pass
#     for opt, arg in opts:
#         if opt == '-h':
#             print 'run.py -d <debug> -p <port> -H <host>'
#             sys.exit()
#         elif opt in ("-i", "--ifile"):
#             inputfile = arg
#         elif opt in ("-o", "--ofile"):
#             outputfile = arg


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"],
            host=app.config["HOST"],
            port=app.config["PORT"],
            threaded=app.config['THREADED'])
