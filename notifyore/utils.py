import os

def get_convore_logo():
    """
    returns a path to file for convore logo
    """

    return os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)),
            'convore_logo.jpg')
