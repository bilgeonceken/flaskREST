from flask import jsonify, Blueprint

from flask_restful import (Resource, Api, inputs, reqparse, fields, abort,
                           marshal, marshal_with, url_for)

import models


review_fields = {
                 "id": fields.Integer,
                 "for_course": fields.String,
                 "rating": fields.Integer,
                 "comment": fields.String(default=""),
                 "created_at": fields.DateTime
                }

def review_or_404(review_id):
    try:
        review = models.Review.get(models.Review.id==review_id)
    except models.Review.DoesNotExist:
        abort(404, message="Review {} does not exist.".format(review_id))
    else:
        return review

def add_course(review):
    review.for_course = url_for("resources.courses.course", id=review.course.id)
    return review

class ReviewList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
                                   "course",
                                   required=True,
                                   help="No course provided",
                                   location=["form", "json"],
                                   type=inputs.positive
                                  )
        self.reqparse.add_argument(
                                   "rating",
                                   required=True,
                                   help="No rating provided",
                                   location=["form", "json"],
                                   type=inputs.int_range(1,5)
                                  )
        self.reqparse.add_argument(
                                   "comment",
                                   required=False,
                                   location=["form", "json"],
                                   default="",
                                   nullable=True
                                  )
        super().__init__()

    def get(self):
        return [marshal(add_course(review), review_fields)
                for review in models.Review.select()]

    @marshal_with(review_fields)    
    def post(self):
        args = self.reqparse.parse_args()
        try:
            review = models.Review.create(**args)
        except models.IntegrityError:
            return jsonify({"message": "Such thing already exists"}) 
        else:
            return add_course(review)
       

class Review(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
                                   "course",
                                   required=True,
                                   help="No course provided",
                                   location=["form", "json"],
                                   type=inputs.positive
                                  )
        self.reqparse.add_argument(
                                   "rating",
                                   required=True,
                                   help="No rating provided",
                                   location=["form", "json"],
                                   type=inputs.int_range(1,5)
                                  )
        self.reqparse.add_argument(
                                   "comment",
                                   required=False,
                                   location=["form", "json"],
                                   default="",
                                   nullable=True
                                  )
        super().__init__()


    @marshal_with(review_fields)
    def get(self, id):
        return add_course(review_or_404(id))
  
    @marshal_with(review_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.Review.update(**args).where(models.Review.id==id)
        query.execute()
                ## this is response body                     ##status code
        return (add_course(review_or_404(id)), 200,
                ## this dictionary, as last argument, includes the headers
                {"Location": url_for("resources.reviews.review", id=id)})

    def delete(self, id):
        query = models.Review.delete(**args).where(models.Review.id==id)
        query.execute()
        ## 204 return code for empty body, if i am not mistaken
        return ("", 204,
                {"Location": url_for("resources.reviews.reviews")})

       
reviews_api = Blueprint("resources.reviews", __name__)
api = Api(reviews_api)
api.add_resource(
                 ReviewList,
                 "/reviews",
                 endpoint="reviews"
                )

api.add_resource(
                 Review,
                 "/reviews/<int:id>",
                 endpoint="review"
                )

