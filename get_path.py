import os
# class GetPath:
#     @classmethod
def getProjectPath():
    curPath = os.path.abspath(os.path.dirname(__file__))
    return curPath