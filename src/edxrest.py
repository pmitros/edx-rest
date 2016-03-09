'''
This is a set of scripts which help us make REST calls into edX Studio APIs.

The APIs used are not official edX-supported APIs

The code is not production-quality. It needs test cases and error handling.
At the very least, it should have a quick look-see at HTTP response status
codes.

But at least downloading courses seems to work. I'll check the rest as
time goes on.
'''

from datetime import datetime
import json
import os
import os.path
import requests
import shutil
import tempfile

from collections import namedtuple

# Sessions are stored in cookies. Each server can have its own cookie
# for this. We just set all the possible ones.
sessionid_strings = ["sessionid",
                     "prod-edge-sessionid"]

# Ditto for CSRF tokens
csrf_token_strings = ["csrftoken",
                      "prod-edx-csrftoken",
                      "prod-edge-csrftoken"]

# Basic cookies we just need to talk to edX
baseline_cookies = {
    "djdt": "hide",
    "edxloggedin": "true",
}

# Basic headers we need just to talk to edX
baseline_headers = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows) AppleWebKit/500"
                  "(KHTML, like Gecko) Chrome/48.0.0.0 Safari/530.00",
}


class METHODS:
    '''
    HTTP Request Methods: GET/POST/PUT/etc.
    '''
    GET = 'get'
    POST = 'post'


class DATA_FORMATS:
    '''
    Data formats for making HTTP headers (accept, etc.)
    '''
    AJAX = 'ajax'
    TARBALL = 'tgz'


class EdXCourse(namedtuple("course_tuple", ["org", "course", "run"])):
    '''
    A helper class to manage edX course URL encoding.

    >>> x=EdXCourse("edx", "edx101", "2000")
    >>> print x.org
    edx
    >>> print x.course_string()
    course-v1:edx+edx101+2000
    '''
    def course_string(self):
        return "course-v1:{org}+{course}+{run}".format(org=self.org,
                                                       course=self.course,
                                                       run=self.run)

if __name__ == "__main__":
    import doctest
    doctest.testmod()


class EdXConnection(object):
    def __init__(self,
                 session=None,
                 server="http://127.0.0.1:8001",
                 csrf="sample_csrf_string"):
        '''
        Initialize a connection to an edX instance. The key parameter is
        session_id. This must be picked out from the network console
        in developer tools in your web browser.
        '''
        if session:
            self.sessionid = session
        else:
            self.sessionid = os.environ['OPEN_EDX_SESSION']
        self.server = server
        self.csrf = csrf

    def compile_header(self,
                       response_format=DATA_FORMATS.AJAX,
                       request_format=DATA_FORMATS.AJAX):
        '''
        This will compile both header and cookies necessary to
        access an edX server as if this were a web browser. The
        key things needed are the session ID cookie. This can
        be grabbed from your browser in the developer tools.
        '''
        header = {}
        cookies = {}

        # Take the baseline cookies
        header.update(baseline_headers)
        cookies.update(baseline_cookies)

        # Add the session ID
        for sid_string in sessionid_strings:
            cookies[sid_string] = self.sessionid

        # Add CSRF protection.
        for csrf_string in csrf_token_strings:
            cookies[csrf_string] = self.csrf
        header['X-CSRFToken'] = self.csrf

        # And we need appropriate content type headers both
        # for what we're sending and what we expect. This is
        # usually JSON, but it's sometimes files.
        if response_format == DATA_FORMATS.AJAX:
            header["Accept"] = "application/json, text/javascript, */*; q=0.01"
        if response_format == DATA_FORMATS.TARBALL:
            pass  # No header needed
        if request_format == 'ajax':
            header["Content-Type"] = "application/json; charset=UTF-8",

        # And more CSRF protection -- we do need the referer
        header["Referer"] = self.server + "/course",
        return (header, cookies)

    def ajax(self,
             url,
             payload=None,
             response_format=DATA_FORMATS.AJAX,
             request_format=DATA_FORMATS.AJAX,
             method=METHODS.POST):
        '''
        Make an AJAX call. This expects both the request and response to be
        JSON.
        '''
        (headers, cookies) = self.compile_header(
            response_format=response_format,
            request_format=request_format
        )
        if request_format == DATA_FORMATS.AJAX and \
           method != METHODS.GET:
            payload = json.dumps(payload)
        if method == METHODS.POST:
            r = requests.post(self.server+url,
                              data=payload,
                              cookies=cookies,
                              headers=headers)
        elif method == METHODS.GET:
            if payload:
                print payload
                raise "Payload doesn't work with get"
            r = requests.get(self.server+url,
                             cookies=cookies,
                             headers=headers)

        if response_format == DATA_FORMATS.AJAX:
            return json.loads(r.text)
        return r
        print r.text

    def create_course(self,
                      course_name='Sample course',
                      course_org='edx',
                      course_number='101',
                      course_run=str(datetime.today().year)):
        '''
        Make a new edX course
        '''
        print "Creating", course_name
        url = "/course/"
        payload = {"org": course_org,
                   "number": course_number,
                   "display_name": course_name,
                   "run": course_run}
        r = self.ajax(url, payload)
        print r.text

    def add_author_to_course(self,
                             course_name,
                             author_email):
        print "Adding", author_email, "to", course_slug
        url = "course_team/{course}/{author_email}"
        url = url.format(course=course,
                         author_email=author_email)
        payload = {"role": "instructor"}
        r = requests.post(url, payload)

    def download_course(self, course, filepointer, close=True):
        '''
        This will download a course as a tarball from an Open edX
        server. This takes a while. Open edX will synchronously make
        the tarball for us.
        '''
        (headers, cookies) = self.compile_header()
        url = "/export/{course}?_accept=application/x-tgz"
        url = url.format(course=course.course_string())
        r = self.ajax(url,
                      response_format=DATA_FORMATS.TARBALL,
                      method=METHODS.GET)
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:  # filter out keep-alive new chunks
                filepointer.write(chunk)
        if close:
            filepointer.close()
