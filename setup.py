import os
import sys

from setuptools import setup, find_packages

DESCRIPTION = 'An extension to Pyglet'

VISUAL_DIR = os.getcwd()
SITE_PACKAGES = os.path.join(VISUAL_DIR, 'site-packages')
excluded = []
# The source dist comes with batteries included, the wheel can use pip to get the rest
is_wheel = 'bdist_wheel' in sys.argv
if is_wheel:
    excluded.append('extlibs.future')


def exclude_package(pkg):
    for exclude in excluded:
        if pkg.startswith(exclude):
            return True
    return False


def create_package_list(base_package):
    return ([base_package] +
            [base_package + '.' + pkg
             for pkg
             in find_packages(base_package)
             if not exclude_package(pkg)])


def main():
    setup(
        name='PygletHelper',
        description=DESCRIPTION,
        author='Catherine Holloway',
        author_email='milankie@gmail.com',
        platforms=['POSIX', 'MacOS', 'Windows'],
        license='other',
        # packages=['vis'],
        package_dir={
            'vis': os.path.join(SITE_PACKAGES, 'vis'),
        },
        requires=[
            'numpy',
            'pyglet'
        ],
        # Package info
        packages=create_package_list('pygletHelper'),
        #py_modules=['util', 'objects'],
        zip_safe=False)


'''
# fetch values from package.xml
setup(
    author='Catherine Holloway',
    author_email='cholloway@clearpathrobotics.com',
    url='https://bitbucket.org/clearpathrobotics/testing_scripts',
    package_dir={'': 'src'},
    py_modules=['BagHelper', 'BagPlayer', 'DataFrameHelper', 'evaluate_rpe', 'GraphingHelper', 'OdomProcessor',
                'RosHelpers'],
    requires=['std_msgs', 'rospy', 'message_filters', 'gps_common', 'sensor_msgs']
)
'''

if __name__ == '__main__':
    main()
