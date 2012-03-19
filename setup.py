from setuptools import setup, find_packages

setup(
    name='django_etherpad_lite',
    version='0.1dev',
    author='Sofian Benaissa',
    url='https://github.com/sfyn/django_etherpad_lite',
    description='Etherpad-lite integration for Django',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Django',
        # Disabled for now, since it's not installable for me right now
        #'pycurl',
        'simplejson'
    ],
    license='GPL3',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
    ],
)
