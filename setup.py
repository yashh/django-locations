from setuptools import setup, find_packages
 
setup(
    name='django-locations',
    version='0.1.0',
    description='A location based social network using Django & Pinax',
    author='Yashh',
    author_email='yash888@gmail.com',
    url='http://code.google.com/p/django-locations/',
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
