import os

from setuptools import Extension, setup

DESCRIPTION = 'An extension to Pyglet'

VISUAL_DIR = os.getcwd()
SITE_PACKAGES = os.path.join(VISUAL_DIR, 'site-packages')

def main():

    setup(
        name='PygletHelper',
        description=DESCRIPTION,
        author='Catherine Holloway',
        author_email='milankie@gmail.com',
        platforms=['POSIX','MacOS','Windows'],
        license='other',
        packages=['vis'],
        package_dir={
            'vis': os.path.join(SITE_PACKAGES,'vis'),
            },
        requires=[
            'numpy',
            #,'wxPython >= 2.9'],
        ],
        zip_safe=False)


if __name__=='__main__':
    main()
