from lib.crowdin import Crowdin, PROJECT_LIST

PROJECT = 'Jackbox Starter Pack UA'
PATH_BUILD = '../build.zip'
PATH_FOLDER = '../build'

if __name__ == '__main__':
    c = Crowdin()
    c.download_last_build(PROJECT_LIST[PROJECT], PATH_BUILD)
    c.unzip_build(PATH_BUILD, PATH_FOLDER)
