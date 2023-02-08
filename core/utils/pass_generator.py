import random
import string

lower = string.ascii_lowercase
upper = string.ascii_uppercase
num = string.digits

all = lower + upper + num


def generator(length):
    return "".join(random.sample(all,length))
