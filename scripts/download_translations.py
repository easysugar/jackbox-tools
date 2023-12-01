import time

from lib.crowdin import Crowdin, PROJECT_LIST

# PROJECT = 'starter'
PROJECT = 'general'
PATH_BUILD = '../build.zip'
PATH_FOLDER = '../build'

if __name__ == '__main__':
    c = Crowdin()
    print('Creating build...')
    c.create_build(PROJECT_LIST[PROJECT])
    time.sleep(20)  # wait until project is building
    print('Downloading build...')
    c.download_last_build(PROJECT_LIST[PROJECT], PATH_BUILD)
    c.unzip_build(PATH_BUILD, PATH_FOLDER)
