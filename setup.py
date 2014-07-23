from setuptools import setup, find_packages

f = open('README.rst')
readme = f.read()
f.close()

setup(
    name='django-cronkite',
    version='1.0.0',
    description='A reusable django application providing a lightweight cron-like distributed task runner.',
    long_description=readme,
    author='Greg Boyington',
    author_email='evilchili@gmail.com',
    url='http://github.com/evilchili/django-cronkite/tree/master',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
