'''
This is a helper script which allows us to make a new course in
edX Studio via AJAX requests. We'd like to script the creation
of the L@S courses. This works, but requires us to manually
pull out the session ID from a log into edX Studio. We'd like
to fix this at some point, but we probably won't.
'''

import json
import os
import os.path
import requests
import shutil
import tempfile

csrf = "[Get this from cookies]"

cookies = {
    "djdt": "hide",
    "edxloggedin": "true",
    "sessionid": "",
    "prod-edge-sessionid":"[Get this from cookies]",
    "prod-edx-sessionid":"[Get this from cookies]",
    "csrftoken": csrf,
    "prod-edx-csrftoken": csrf,
    "prod-edge-csrftoken": csrf
}

headers = {
    "Referer": "https://studio.edge.edx.org/course",
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRFToken": csrf,
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01"
}


file_headers = {
    "Referer": "https://studio.edge.edx.org/course",
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRFToken": csrf,
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01"
}


def create_course(course_name, course_slug):
    print "Creating", course_name
    url = "https://studio.edge.edx.org/course/"
    payload = {"org": "LAS",
               "number": course_slug,
               "display_name": course_name,
               "run": "2016"}
    r = requests.post(url,
                      data=json.dumps(payload),
                      cookies=cookies,
                      headers=headers)
    print r.text

def add_author_to_course(course_slug, author_email):
    print "Adding", author_email, "to", course_slug
    url = "https://studio.edge.edx.org/course_team/course-v1:LAS+{course_slug}+2016/{author_email}"
    url = url.format(course_slug = course_slug, author_email = author_email)
    payload = {"role": "instructor"}
    r = requests.post(url,
                      data=json.dumps(payload),
                      cookies=cookies,
                      headers=headers)

def upload_template_course(course_name, course_slug):
    print "Importing", course_name, course_slug
    base_dir = tempfile.mkdtemp()+"/las-template"
    print base_dir
    shutil.copytree("/home/pmitros/src/las-template/", base_dir)
    for filename in ['/course/course.xml',
                 '/course/problem/A_quick_quiz.xml']:
        base = open(base_dir+"/"+filename+".tmpl").read()
        formatted = base.replace("{slug}", course_slug).replace("{name}", course_name)
        f = open(base_dir+"/"+filename, "w")
        f.write(formatted)
        f.close()
    for filename in ["/course/html/Main_Presentation.html",
                 "/course/html/Abstract_0.html",
                 "/course/html/Other_papers_1.html",
                 "/course/html/Our_supplementary_resources_0.html",
                 "/course/html/Intake_0.html",
                 "/course/html/Supplementary_Resources_0.html",
                 "/course/problem/A_quick_quiz.xml"]:
        new_name = base_dir+os.path.dirname(filename)+"/"+course_slug+"_"+os.path.basename(filename)
        shutil.move(base_dir+filename, new_name)

    url = "https://studio.edge.edx.org/import/course-v1:LAS+{course_slug}+2016"
    url = url.format(course_slug = course_slug)
    os.chdir(base_dir)
    cmd = "tar cfvz course.tar.gz course"
    print "Running", cmd
    os.system(cmd)
    files = {'course-data': ("course.tar.gz", open("course.tar.gz", "rb").read(), "application/gzip", {})}
    r = requests.post(url,
                      files=files,
                      cookies=cookies,
                      headers=file_headers)
    print r.text

for line in open("course_list_done.csv"):
    line = line.split('\t')
    course_slug = line[0]
    course_name = line[1]
    course_authors = [x.strip() for x in line[2].split(",")]
    create_course(course_name, course_slug)
    create_course("Scratchpad for "+course_name, "SCRATCH_"+course_slug)
    upload_template_course(course_name, course_slug)
    for author_email in course_authors:
        add_author_to_course(course_slug, author_email)
        add_author_to_course("SCRATCH_"+course_slug, author_email)
