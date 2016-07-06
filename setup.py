# -*- coding: utf-8 -*-


from setuptools import setup

setup(
    name='jenkins-yml',
    version='1.4',
    entry_points={
        'console_scripts': ['jenkins-yml-runner=jenkins_yml:console_script'],
        'jenkins_yml.runners': ['unconfined=jenkins_yml:unconfined'],
    },
    extras_require={
        'release': ['wheel', 'zest.releaser'],
    },
    install_requires=[
        'pyyaml',
    ],
    py_modules=['jenkins_yml'],
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
