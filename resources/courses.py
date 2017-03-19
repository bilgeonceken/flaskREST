from flask import jsonify, Blueprint
from flask_restful import (Resource, Api, reqparse, inputs, fields,
                            marshal, marshal_with, url_for, abort)
import models

## This dictionary describes all of the fields
## that we want to include when our api gives a resource
course_fields = {
                 "id": fields.Integer,
                 "title": fields.String,
                 "url": fields.String,
                            ## means: list of strings
                            ## list of urls does not work well(fields.url)
                 "reviews": fields.List(fields.String)
                }

## on get function of CourseList we wrap courses with this function to
## attach its reviews to it. otherwise in the response it is  "reviews": "NULL"
def add_reviews(course):
                     ## url_for(resource, **values)
                     ##    generates a URL to given resource
    course.reviews = [url_for("resources.reviews.review", id=review.id)
                      for review in course.review_set]
    return course

def course_or_404(course_id):
    try:
        course = models.Course.get(models.Course.id==course_id)
    except models.Course.DoesNotExist:
        ## you can't pass custom message to flask's abort but you can
        ## to flask-restful's abort.
        abort(404, message="Course {} does not exist.".format(course_id))
    else:
        return course

## Resource for a listof courses
class CourseList(Resource):
    def __init__(self):
        ## we use reqparse module to parse and validate incoming requests
        ## what we do in this part is quite smilar to forms library.

        ## defines self.reqparse as our parser object
        self.reqparse = reqparse.RequestParser()

        ## type="string" by default so no need to specify
        self.reqparse.add_argument(
                                   "title",
                                   required=True,
                                   help="No course title provided",
                                ## we need to tell reqparse where to look
                                ## for this data. It may look in form encoded
                                ## data or look in a json data which is in the
                                ## body of the request. The one comes last in
                                ## the location list, it looks at first.
                                ## form is not form data it is x-www-urlencoded
                                   location=["form", "json"]
                                  )

        self.reqparse.add_argument(
                                   "url",
                                   required=True,
                                   help="No course URL provided",
                                   location=["form", "json"],
                                   ## inputs.url returns the url if valid,
                                   ## raises ValueError if not
                                   type=inputs.url
                                  )
        ## this makes sure strandart setup goes ahead and happens.
        ## says the instructor but i did not get it
        super().__init__()

    def get(self):
        ## if we just define courses = models.Course.select()
        ## return it, we get an error saying that courses
        ## object is not json serializable. to handle that we use marshal.
        ## Whe you are using marshall you provide record(s) and field(s) for
        ## that resource. And there is a for loop because we have to do it
        ## for all courses
        courses =[marshal(add_reviews(course), course_fields)
                  for course in models.Course.select()]
        return jsonify({"courses": courses})


    def post(self):
        args = self.reqparse.parse_args()
        try:
            course = models.Course.create(**args)
        except models.IntegrityError:
            return jsonify({"message": "Such thing already exists"})
        else:
            ## 201: "created" status code
            return (marshal(add_reviews(course), course_fields), 201,
                    {"Location": url_for("resources.courses.course",
                    id=course.id)}
                   )


class Course(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
                                   "title",
                                   required=True,
                                   help="No course title provided",
                                   location=["form", "json"]
                                  )

        self.reqparse.add_argument(
                                   "url",
                                   required=True,
                                   help="No course URL provided",
                                   location=["form", "json"],
                                   type=inputs.url
                                  )
        super().__init__()

    ## same purpose with marshal(), but this one is easier at this situation
    ## where we have only one return value.
    ## takes the returned record and marshals that with given fields
    @marshal_with(course_fields)
    ## We have also "id", here because
    ## individual courses should always get an id
    def get(self, id):
        return add_reviews(course_or_404(id))

    @marshal_with(course_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.Course.update(**args).where(models.Course.id==id)
        query.execute()
                ## this is response body                     ##status code
        return (add_reviews(models.Course.get(models.Course.id==id)), 200,
                ## this dictionary, as last argument, includes the headers
                {"Location": url_for("resources.courses.course", id=id)})

    def delete(self, id):
        query = models.Course.delete(**args).where(models.Course.id==id)
        query.execute()
        ## 204 return code for empty body, if i am not mistaken
        return ("", 204,
                {"Location": url_for("resources.courses.courses")})


courses_api = Blueprint("resources.courses", __name__)
api = Api(courses_api)

## you do not "have to" provide an  endpoint name,
## flask_restful automatically lowercases the
## name of the course and makes it the endpoint
api.add_resource(CourseList,
                 "/api/v1/courses",
                 endpoint="courses"
                )

api.add_resource(Course,
                 "/api/v1/courses/<int:id>",
                 endpoint="course"
                )
