from setuptools import setup, find_packages
 
setup(
    name='django-locations',
    version='0.1.1',
    description='A location based social network using Django & Pinax',
    author='Yashwanth Nelapati',
    author_email='yash888@gmail.com',
    url='http://github.com/yashh/django-locations/commits/master',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
