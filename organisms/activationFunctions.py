# Defines activation functions consider Maths library
import math


# TODO: define in scipy or numpy or something with vectorization unless Cython optimizes appropriately
#               (starting to sound like benchmark activities..)


def softmax(signal):
    """
    currently only supporting softmax
    """
    # TODO: adjust inflection points by the softmax (4 or whatever) from k stanley
    return 1.0 / (1.0 + math.exp(-signal))
