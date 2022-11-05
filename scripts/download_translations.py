from lib.crowdin import Crowdin, PROJECT_LIST

PROJECT = 'Jackbox Starter Pack UA'

if __name__ == '__main__':
    c = Crowdin()
    c.download_last_build(PROJECT_LIST[PROJECT])
    c.unzip_build()
