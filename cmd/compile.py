import yaml
import os.path
import tarfile

import edxrest

config = yaml.load(open(os.path.expanduser('~')+"/edxrest.yaml"))

omit = [
    'course',
    'course/about'
    'course/about/overview.html'
    'course/assets',
    'course/chapter',
    'course/course.xml',
    'course/html',
    'course/info',
    'course/info',
    'course/info/updates.html',
    'course/info/updates.items.json',
    'course/policies',
    'course/policies/assets.json',
    'course/policies/course',
    'course/policies/course/grading_policy.json',
    'course/policies/course/policy.json',
    'course/problem'
    'course/sequential',
    'course/vertical',
]

course_nums = [x.split('\t')[0] for x in
               open("/home/pmitros/src/las-template/scripts/course_list_done.csv").readlines()]

connection = edxrest.EdXConnection(
    server = "https://studio.edge.edx.org/",
    session = config['session'],
    csrf = config['csrf']
)

duplicates = []

os.mkdir('course')
for num in course_nums:
    print num
    filename = num+".tar.gz"
    connection.download_course(edxrest.EdXCourse('LAS', num, "2016"),
                               open(filename, "w"))
    tf = tarfile.open(filename)
    for member in tf.getmembers():
        if member.name in omit:
            continue
        if os.path.exists(member.name):
            duplicates.append(member.name)
            continue
        print member.name
        tf.extract(member)

print "Duplicates:", duplicates
