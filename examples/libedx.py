from edxrest import EdXConnection, EdXCourse

sid = "[Get this from course]"
csrf = "[Get this from course]"

c = EdXConnection(session = sid,
                  csrf = csrf)
course = EdXCourse("edX","DemoX", "Demo_Course")
print course.course_string()
#fp = open("out.tgz", "wb")
#c.download_course(course, fp)

course = EdXCourse("edx", "upload_test", "2")
c.create_course(course, "Upload test")
c.add_author_to_course(course, "audit@example.com")
#http://localhost:8001/course_team/course-v1:edx+upload_test+2/staff@example.com
#http://localhost:8001/course_team/course-v1:edx+upload_test+2/verified@example.com
