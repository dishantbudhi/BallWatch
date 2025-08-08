from flask import Blueprint, request, jsonify, make_response, current_app, redirect, url_for
import json
from backend.db_connection import db

games = Blueprint('players', __name__)


@games.route('/games', methods=['GET'])
def get_games():
    current_app.logger.info('GET /games handler')
    cursor = db.get_db().cursor()

    cursor.execute('SELECT * FROM Game')
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response

@games.route('/games', methods=['POST'])
def create_game():
    cursor = db.get_db().cursor()
    current_app.logger.info('POST /games handler')

    new_game = request.get_json()

    cursor.execute('''INSERT INTO Game (name, genre, release_date) VALUES (?, ?, ?)''',
                   (new_game['name'], new_game['genre'], new_game['release_date']))
    db.get_db().commit()

    the_response = make_response(jsonify(new_game), 201)
    return the_response

"""
INSERT INTO Game (date, season, is_playoff, home_team_id, away_team_id, home_score, away_score) VALUES
('2025-01-15', '2024-25', FALSE, 1, 2, 118, 112),



# ------------------------------------------------------------
# This is a POST route to add a new product.
# Remember, we are using POST routes to create new entries
# in the database. 
@products.route('/product', methods=['POST'])
def add_new_product():
    
    # In a POST request, there is a 
    # collecting data from the request object 
    the_data = request.json
    current_app.logger.info(the_data)

    #extracting the variable
    name = the_data['product_name']
    description = the_data['product_description']
    price = the_data['product_price']
    category = the_data['product_category']
    
    query = f'''
        INSERT INTO products (product_name,
                              description,
                              category, 
                              list_price)
        VALUES ('{name}', '{description}', '{category}', {str(price)})
    '''
    # TODO: Make sure the version of the query above works properly
    # Constructing the query
    # query = 'insert into products (product_name, description, category, list_price) values ("'
    # query += name + '", "'
    # query += description + '", "'
    # query += category + '", '
    # query += str(price) + ')'
    current_app.logger.info(query)

    # executing and committing the insert statement 
    cursor = db.get_db().cursor()
    cursor.execute(query)
    db.get_db().commit()
    
    response = make_response("Successfully added product")
    response.status_code = 200
    return response
"""