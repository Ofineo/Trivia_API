import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection, pagination=QUESTIONS_PER_PAGE):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * pagination
  end = start + pagination

  questions = [question.format() for question in selection]
  paginated_questions = questions[start:end]

  return paginated_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  cors = CORS(app, resources={r"127.0.0.1/*":{"origins":"*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    return response

  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    paginated_questions = paginate_questions(request,questions)

    categories = Category.query.all()
    
    if len(paginated_questions) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'totalQuestions': len(Question.query.all()),
      'categories': [c.type for c in categories],
      'currentCategory': ''
    })

  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):

    categories = Category.query.all()
    
    if id <= len(categories):
      questions = Question.query.join(Category, Question.category==id+1).all()
      paginated_questions = paginate_questions(request,questions)

      return jsonify({
        'success': True,
        'questions': paginated_questions,
        'totalQuestions': len(questions),
        'currentCategory': id+1
      })
    else:
      abort(400)


  @app.route('/categories')
  def get_categories():

    categories = Category.query.all()
    
    return jsonify({
      'success': True,
      'categories': [c.type for c in categories]
    })

  @app.route('/add', methods=['POST'])
  def post_new_question():

    try:
      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_difficulty = body.get('difficulty', None)
      new_category = int(body.get('category', None))

      question = Question(question = new_question, answer = new_answer, difficulty= new_difficulty, category= str(new_category+1))

      question.insert()

      return jsonify({
        'success': True,
        'question': question.format()
      })
    except:
      abort(422)

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.get(id)

    if question is None:
      abort(404)

    try:
      question.delete() 
      return jsonify({
      'success': True
      })
    except:
      abort(422)

  @app.route('/questions/<searchTerm>', methods=['POST'])
  def search_questions(searchTerm):
    questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
    paginated_questions = paginate_questions(request,questions)
    
    if len(paginated_questions) == 0:
      abort(404)
    
    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'totalQuestions': len(questions),
      'currentCategory': ''
    })

  @app.route('/quizzes', methods=['POST'])
  def play_game():
    body = request.get_json()
    category = int(body.get('quiz_category'))+1

    previous_questions = body.get('previous_questions')

    if len(previous_questions) == len(Question.query.join(Category, Question.category==category).all()):
      return jsonify({
      'success': True,
      'question': False
      })
    elif len(previous_questions):
      questions = Question.query.join(Category, Question.category==category).filter(~Question.id.in_(previous_questions)).first()
    else:
      questions = Question.query.join(Category, Question.category==category).first()
    
    paginated_questions = questions.format()
  
    return jsonify({
      'success': True,
      'question': paginated_questions
    })

 
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405
  
  return app