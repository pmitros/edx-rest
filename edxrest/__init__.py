'''
This is a library which help us make REST calls into edX Studio APIs.

The APIs used are not official edX-supported APIs

The code is **not** production-quality. It needs test cases and error
handling.  At the very least, it should have a quick look-see at HTTP
response status codes.

But it does work.
'''


from .edxrest import METHODS, DATA_FORMATS, EdXCourse, EdXConnection
