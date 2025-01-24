#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe
from werkzeug.security import generate_password_hash, check_password_hash

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {"error": "Username and password are required"}, 422

        new_user = User(username=username)
        new_user.password = password  # Set password using setter
        db.session.add(new_user)
        try:
            db.session.commit()
            return new_user.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username already exists"}, 409

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {'error': 'No user logged in'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        if 'user_id' not in session:
            return {'error': 'No user logged in'}, 401

        session.pop('user_id', None)
        return {'message': 'Logged out successfully'}, 204

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized access'}, 401

        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return [recipe.to_dict() for recipe in recipes], 200

    def post(self):
        data = request.get_json()
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized access'}, 401

        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        new_recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=user_id
        )

        db.session.add(new_recipe)
        try:
            db.session.commit()
            return new_recipe.to_dict(), 201
        except IntegrityError as e:
            db.session.rollback()
            return {'error': str(e)}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
# In this snippet, we have a few classes that inherit from Resource. Each class represents a different endpoint in our API. The Signup class is responsible for creating new users, the Login class is responsible for authenticating users, the Logout class is responsible for logging users out, and the RecipeIndex class is responsible for managing recipes.