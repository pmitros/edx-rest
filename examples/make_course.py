

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

for line in open("course_list.csv"):
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

#Thank you. We've created two courses -- one for your paper and one if you'd like a safe place to explore the edX platform. You should have access to both. Let me know if you run into any issues (the course creation is all scripted, and it's our first time doing something like this, so it's possible there might still be rough edges/bugs).
