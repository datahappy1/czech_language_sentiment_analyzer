import os

if os.environ.get('DATABASE_URL'):
    __env__ = 'remote'
else:
    __env__ = 'local'
