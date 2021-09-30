import os
import subprocess
import traceback
from mimetypes import guess_type
from time import time

from reportportal_client import ReportPortalServiceAsync
from conf.reportportal import *


def timestamp():
    return str(int(time() * 1000))


def my_error_handler(exc_info):
    """
    This callback function will be called by async service client when error occurs.
    Return True if error is not critical and you want to continue work.
    :param exc_info: result of sys.exc_info() -> (type, value, traceback)
    :return:
    """
    print("Error occurred: {}".format(exc_info[1]))
    traceback.print_exception(*exc_info)


service = ReportPortalServiceAsync(endpoint=endpoint, project=project,
                                   token=token, error_handler=my_error_handler)

# Start launch.
launch = service.start_launch(name=launch_name,
                              start_time=timestamp(),
                              description=launch_doc)

# Start test item.
test = service.start_test_item(name="三星A9S",
                               description="2b400091a21d7ece",
                               tags=["Monkey", "Smoke"],
                               start_time=timestamp(),
                               item_type="STEP",
                               parameters={"key1": "val1",
                                           "key2": "val2"})

# Create text log message with INFO level.
service.log(time=timestamp(),
            message="Crash info",
            level="INFO")

# Create log message with attached text output and WARN level.
crash_log = "phone3_crash_logcat_20200115103802.log"
with open(crash_log, "rb") as cf:
    attachment = {
                "name": os.path.basename(crash_log),
                "data": cf.read(),
                "mime": guess_type(crash_log)[0] or "application/octet-stream"
            }
    service.log(time=timestamp(),
            message="Find Crash!",
            level="WARN", attachment=attachment
            # attachment={
            #     "name": "crash.log",
            #     "data": subprocess.check_output("free -h".split()),
            #     "mime": "text/plain"
            # }
            )

# Create log message with binary file, INFO level and custom mimetype.
# image = "/tmp/image.png"
# with open(image, "rb") as fh:
#     attachment = {
#         "name": os.path.basename(image),
#         "data": fh.read(),
#         "mime": guess_type(image)[0] or "application/octet-stream"
#     }
#     service.log(timestamp(), "Screen shot of issue.", "INFO", attachment)

# Create log message supplying only contents
# service.log(
#     timestamp(),
#     "running processes",
#     "INFO",
#     attachment=subprocess.check_output("ps aux".split()))

# Finish test item.
service.finish_test_item(end_time=timestamp(), status="PASSED")

# Finish launch.
service.finish_launch(end_time=timestamp())

# Due to async nature of the service we need to call terminate() method which
# ensures all pending requests to server are processed.
# Failure to call terminate() may result in lost data.
service.terminate()