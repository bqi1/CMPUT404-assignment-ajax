#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, redirect, url_for, jsonify
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        self.cleared = False
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space
    def iscleared(self):
        return self.cleared
    def set_cleared(self,cleared):
        self.cleared = cleared
    def get_cleared(self):
        return self.cleared
    def replace_space(self,newspace):
        self.space = newspace

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()          

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return redirect("/static/index.html", code = 301)



@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    data = flask_post_json()
    if type(data) is dict and 'x' in data and 'y' in data:
        myWorld.set(entity,data)
        response = jsonify(data)
        response.status_code = 200
    else:
        response = jsonify(success = False)
        response.status_code = 400
    return response


@app.route("/worldDifference", methods=['POST','GET'])    
def worldDifference():
    '''returns a 2 item list. first item is whether world is cleared, second item is list of entities to add '''
    client_world = flask_post_json()
    if not myWorld.world():    # IF WORLD IS EMPTY, RETURN EMPTY WORLD WITH BOOLEAN AS TRUE. ELSE
        myWorld.set_cleared(True)
    else:
        myWorld.set_cleared(False)
    # FOr each thing in myworld, if not in client's world, add in
    to_add = []
    for point_key in myWorld.world().keys():
        if point_key in client_world and client_world[point_key] == myWorld.world()[point_key]:
            continue
        else:
            to_add.append((point_key,myWorld.world()[point_key]))
    response = jsonify((myWorld.get_cleared(),to_add))
    response.status_code = 200
    return response

@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''

    if flask.request.method == 'POST':
        potential_world_dict = flask_post_json()
        if type(potential_world_dict) is dict:
            myWorld.replace_space(potential_world_dict)
    response = jsonify(myWorld.world())
    response.status_code = 200
    return response

@app.route("/entity/<entity>")    
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    try:
        response = jsonify(myWorld.get(entity))
        response.status_code = 200
    except KeyError:
        response = jsonify(found = False)
        response.status_code = 200
    return response
@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    response = jsonify(myWorld.world())
    response.status_code = 200
    return response
if __name__ == "__main__":
    app.run()
