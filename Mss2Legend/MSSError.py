import sys

def BailOut( errorMessage, params=None):
    '''
    Prints an error message and exits the program.
    The errorMessage may contain %-place holders, 
    and the params is a tuple with entries to insert.
    '''

    if params:
        errorMessage = errorMessage % params
        
    print( "ERROR:", errorMessage)
    sys.exit( 1)

