"""
.. module:: GVRlib.sql
   :platform: Unix, Windows
   :synopsis: Import of SQL libraries.
This module contains the code necessary to import libraries related to SQL.
"""


import sys
import os

thirdparty = None
if __package__ is not None:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    import importlib
    try:
        thirdparty = importlib.import_module('3rdparty')
    except ImportError:
        thirdparty = None
    else:
        module = 'pymysql'
        try:
            pr = __import__(module, fromlist = ['*'])
        except:
            dirpath = os.path.dirname(os.path.abspath(__file__))
            basedir = os.path.basename(dirpath)
            try:
                pr = __import__(basedir + '.' + module, fromlist = ['*'])
            except:
                dirpath = os.path.dirname(dirpath)
                basedir = os.path.basename(dirpath) + '.' + basedir
                pr = __import__(basedir + '.' + module, fromlist = ['*'])
        for k in dir(pr):
            globals()[k] = getattr(pr, k)
if thirdparty is None:
    from pymysql import *
