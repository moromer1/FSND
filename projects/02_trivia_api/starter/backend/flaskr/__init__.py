import os
from sre_parse import CATEGORIES
from types import new_class
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy.sql.expression import null, select

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):

    items_limit = request.args.get('limit', 10, type=int)
    selected_page = request.args.get('page', 1, type=int)
    current_index = selected_page - 1

    questions = Question.query.order_by(
        Question.id).limit(items_limit).offset(
        current_index * items_limit).all()

    start = (selected_page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [Question.format() for Question in selection]
    current_questions = questions[start: end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins
  '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization, true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response
    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def get_categories():

        try:
            categories = Category.query.all()

            if len(categories) == 0:
                abort(404)

            arr_categories = {}
            for category in categories:
                arr_categories[category.id] = category.type

            return jsonify({
                'success': True,
                'categories': arr_categories,
                'total_categories': len(categories),

            })

        except BaseException:
            if len(categories) == 0:
                abort(404)
            else:
                abort(422)
    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the
  bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    def get_questions():

        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            if len(current_questions) == 0:
                abort(404)

            categories = Category.query.all()
            arr_categories = {}
            for category in categories:
                arr_categories[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'categories': arr_categories
            })
        except BaseException:
            if len(current_questions) == 0:
                abort(404)
            else:
                abort(422)

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.
  TEST: When you click the trash icon next to a question,
  the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })

        except BaseException:
            if question is None:
                abort(404)
            else:
                abort(422)

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions/add', methods=['POST'])
    def create_question():

        body = request.get_json()
        new_q = body.get('question', None)
        new_ans = body.get('answer', None)
        new_dif = body.get('difficulty', None)
        new_cat = body.get('category', None)

        if {
          new_q is None or new_ans is None or
          new_cat is None or new_dif is None}:
            abort(400)
        else:
            question = Question(
                question=new_q,
                answer=new_ans,
                difficulty=new_dif,
                category=new_cat
            )

        try:
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except BaseException:
            if {
              new_q is None or new_ans is None or
              new_cat is None or new_dif is None}:
                abort(400)
            else:
                abort(422)

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/questions/search', methods=['POST'])
    def search_question():

        data = request.get_json()
        search_term = data.get('searchTerm')

        try:
            if search_term:
                questions = Question.query.filter(
                    Question.question.ilike(
                        '%{}%'.format(
                            data['searchTerm']))).all()

                current_questions = paginate_questions(request, questions)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions)
                })

        except BaseException:
            abort(422)

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):

        try:
            questions = Question.query.filter_by(
                category=str(category_id)).all()

            if len(questions) == 0:
                abort(404)

            question_list = []
            for q in questions:
                question_list.append(q.format())

            return jsonify({
                'success': True,
                'questions': question_list,
                'total_questions': len(question_list),
                'current_category': category_id

            })

        except BaseException:
            if len(questions) == 0:
                abort(404)

            else:
                abort(422)

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():

        body = request.get_json()
        previous_q = body['previous_questions']
        category_id = body['quiz_category']['id']
        category_id = (int(category_id) + 1)

        if category_id == 0:
            if previous_q is not None:
                questions = Question.query.filter_by(
                    category=category_id['id']).all()
            else:
                questions = Question.query.all()
        else:
            if previous_q is not None:
                questions = Question.query.filter(
                    Question.id.notin_(previous_q),
                    Question.category == category_id).all()
            else:
                questions = Question.query.filter_by(
                    category=category_id['id']).all()

        if len(questions) != 0:
            next_question = random.choice(questions).format()
            if not next_question:
                abort(404)
            if next_question is None:
                next_question = False
            return jsonify({
                'success': True,
                'question': next_question
            })

        else:
            return jsonify({
                'success': True,
                'question': False})

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    return app
