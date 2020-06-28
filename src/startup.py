import vkquick as vq

from .db import post


@vq.Signal("startup")
def startup():
    """
    Handler to signal `startup`
    """
    with open("src/db.sql") as file:
        post(file.read())
