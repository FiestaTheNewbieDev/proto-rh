'''
Allows for creating and obtaining a synchronized Base instance.
'''
from sqlalchemy.ext.declarative import declarative_base

# Create the Base instance
Base = declarative_base()


def get_base():
    '''
    Return the Base instance.
    '''

    return Base
