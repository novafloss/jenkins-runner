# -*- coding: utf-8 -*-


from setuptools import setup

setup(
    name='jenkins-runner',
    version='0.1.dev0',
    entry_points={
        'console_scripts': ['jenkins-runner=jenkins_runner:entrypoint'],
    },
    extras_require={
        'release': ['wheel', 'zest.releaser'],
    },
    install_requires=[
        'pyyaml',
    ],
    py_modules=['jenkins_runner'],
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
    url='https://github.com/novafloss/jenkins-runner',
)
