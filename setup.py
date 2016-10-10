# coding: utf-8

from setuptools import setup


setup(
    name='jenkins-yml',
    version='2.22',
    entry_points={
        'console_scripts': ['jenkins-yml-runner=jenkins_yml:runner_script'],
        'jenkins_yml.runners': ['unconfined=jenkins_yml.runner:unconfined'],
    },
    extras_require={
        'release': ['wheel', 'zest.releaser'],
        'renderer': ['jinja2'],
    },
    install_requires=[
        'pyyaml',
    ],
    packages=['jenkins_yml'],
    package_data={
        'jenkins_yml': ['templates/*'],
    },
    description='Define Jenkins jobs from repository',
    author=u'Étienne BERSAC',
    author_email='etienne.bersac@people-doc.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    keywords=['jenkins'],
    license='GPL v3 or later',
    url='https://github.com/novafloss/jenkins-yml',
)
