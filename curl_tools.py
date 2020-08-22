import pycurl
import json
import os
import sys
import certifi
from io import BytesIO
import urllib.parse


def test(debug_type, debug_msg):
    print("debug(%d): %s" % (debug_type, debug_msg))


# pretty print progress and percentage completed
# def progress(download_t, download_d, upload_t, upload_d):
#     if download_t:
#          percent_completed = float(download_d) / float(download_t)  # You are calculating amount uploaded
#          rate = round(percent_completed * 100, ndigits=2)  # Convert the completed fraction to percentage
#          print('(%s%%) -- %s of %s' % (rate, str(int(download_d/1000000)), str(int(download_t/1000000)) + 'MB'), end='\n', flush=True)

def curl_command(base_url, header_list, post_put_get, output_dir=None, filename=None, input_dict=None,
                 user_name=None, password=None, encode=False, debug=False):
    c = pycurl.Curl()
    # print('Setting Base URL..')
    c.setopt(pycurl.CAINFO, certifi.where())
    c.setopt(c.URL, base_url)
    # print('Setting header..')
    c.setopt(c.HTTPHEADER, header_list)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    # c.setopt(c.SSLVERSION, c.SSLVERSION_SSLv2)
    c.setopt(c.NOPROGRESS, False)
    # c.setopt(c.XFERINFOFUNCTION, progress)
    c.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_0) # fixes (18, 'transfer closed with outstanding read data remaining')

    if user_name or password:
        # print('Setting HTTP auth..')
        c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
        c.setopt(pycurl.USERPWD, user_name + ':' + password)
        # print(user_name + ':' + password)

    # if encode is True:
    #     input_dict = urllib.parse.urlencode(input_dict).encode()

    if post_put_get == 'POST':
        c.setopt(pycurl.POST, 1)
        if encode is True:
            action_data = urllib.parse.urlencode(input_dict).encode()
        else:
            action_data = json.dumps(input_dict)
        c.setopt(pycurl.POSTFIELDS, action_data)

    if post_put_get == 'PUT':
        if encode is True:
            action_data = urllib.parse.urlencode(input_dict).encode()
        else:
            action_data = json.dumps(input_dict)
        c.setopt(pycurl.CUSTOMREQUEST, "PUT")
        c.setopt(pycurl.POSTFIELDS, action_data)

    response_str = BytesIO()
    c.setopt(pycurl.WRITEFUNCTION, response_str.write)

    header_str = BytesIO()
    c.setopt(pycurl.HEADERFUNCTION, header_str.write)

    if debug == 'True':
        c.setopt(pycurl.DEBUGFUNCTION, test)
        c.setopt(pycurl.VERBOSE, 1)

    if filename:
        attempts = 5
        while attempts != 0:
            file_path = os.path.join(output_dir, filename)
            with open(file_path, 'wb') as f:
                c.setopt(c.WRITEDATA, f)
                c.perform()
                c.close()
            if os.path.isfile(file_path):
                attempts = 0
            else:
                attempts -= 1
                print('Retrying download..')
    else:
        tries = 5
        if debug:
            print('Submitting curl command..')

        try:
            c.perform()
        except:
            if debug:
                print('Command failed, retrying..')
            tries -= 1
            if tries > 0:
                c.perform()

        c.close()

    header_result = header_str.getvalue().decode('UTF-8').rstrip('\n')

    if filename:
        response_result = None
    else:
        try:
            resp_decoded = response_str.getvalue().decode('UTF-8').replace('\n', '')
            response_result = json.loads(resp_decoded)
            # print('pause')
        except ValueError:
            print('CURL ERROR!:')
            print(resp_decoded)
            sys.exit()

    return {'header_result': header_result, 'response_result': response_result, 'request_string': input_dict,
            'url': base_url}
