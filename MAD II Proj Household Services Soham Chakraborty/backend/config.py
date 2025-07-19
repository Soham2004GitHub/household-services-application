from passlib.hash import bcrypt

import os
from flask import Flask, request, jsonify

class Config():
    DEBUG = False
    SQL_ALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    DEBUG = True
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = 'thisshouldbekeptsecret'
    SECRET_KEY = "shouldbekeyveryhidden"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'

    SECURITY_LOGIN_URL = '/login'
    SECURITY_LOGOUT_URL = '/logout'
    SECURITY_REGISTER_URL = '/register'

    CACHE_TYPE =  "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 30 #30 seconds
    CACHE_REDIS_PORT = 6379 #The redis port no. configured (anyway default for Redis is always 6379)

    



    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max file size: 16 MB
    

    WTF_CSRF_ENABLED = False