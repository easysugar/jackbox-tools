import time

from lib.crowdin import Crowdin, PROJECT_LIST

# PROJECT = 'Jackbox Starter Pack UA'
PROJECT = 'Jackbox UA'
PATH_BUILD = '../build.zip'
PATH_FOLDER = '../build'

if __name__ == '__main__':
    c = Crowdin()
    c.create_build(PROJECT_LIST[PROJECT])
    time.sleep(10)  # wait until project is building
    c.download_last_build(PROJECT_LIST[PROJECT], PATH_BUILD)
    c.unzip_build(PATH_BUILD, PATH_FOLDER)
