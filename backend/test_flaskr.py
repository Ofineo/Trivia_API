import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question':'Who rules the world?', 
            'answer': 'Satan 1 John 5:19', 
            'difficulty': '5', 
            'category': '4' 
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        question = Question.query.filter(Question.answer=='Satan 1 John 5:19').one_or_none()
        if question:
            res = self.client().delete(f'/questions/{question.id}')

        pass
    
    def test_get_all_books(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        categories = Category.query.all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['categories'], [category.type for category in categories])

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['currentCategory'], 4+1)

    def test_add_question(self):
        res = self.client().post('/add', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_delete_question(self):

        self.client().post('/add', json=self.new_question)

        question = Question.query.filter(Question.answer=='Satan 1 John 5:19').one_or_none()

        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)
        
        questions = Question.query.all()
        
        self.assertFalse(question.id in questions)

     def test_search(self):

        search_term = 'man'

        res = self.client().post(f'/questions/{search_term}')
        data = json.loads(res.data)

        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).count()
        
        self.assertEqual(data['totalQuestions'],questions)

    def test_400_failed_get_questions_by_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')
    
    def test_404_delete_nonexistent_question(self):
        res = self.client().delete(f'/questions/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()