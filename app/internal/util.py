import random
import string

RANDOM_STRING_LENGTH = 16


def generate_random_string(length: int = RANDOM_STRING_LENGTH):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string
