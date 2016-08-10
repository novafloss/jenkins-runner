from unittest import TestCase


class TestYml(TestCase):
    def test_empty_defaults(self):
        from jenkins_yml import Job

        yml = "freestyle: test command"
        jobs = list(Job.parse_all(yml))
        assert 1 == len(jobs)
        job = jobs[0]
        assert 'freestyle' == job.name
        assert job.config

    def test_with_defaults(self):
        from jenkins_yml import Job

        yml = "freestyle: test command"
        defaults = dict(
            github_repository='https://github.com/owner/repository',
            scm_credentials='github-https',
            node='slave1',
        )
        jobs = list(Job.parse_all(yml, defaults))
        assert 1 == len(jobs)
        job = jobs[0]
        assert 'slave1' == job.config['node']


class TestXml(TestCase):
    def test_parse(self):
        from jenkins_yml import Job

        xml = Job(name='freestyle', config=dict(
            node='slave',
            github_repository='https://github.com/owner/repo',
            scm_credentials='CREDS',
            set_commit_status=True,
        )).as_xml()

        job = Job.from_xml('freestyle', xml)

        assert 'CREDS' == job.config['scm_credentials']
        assert job.config['set_commit_status']
        assert 'slave' == job.config['node']

    def test_parse_axis(self):
        from jenkins_yml import Job

        xml = Job(name='matrix', config=dict(
            node='slave-legacy',
            axis=dict(AXIS1=['val1', 'val2']),
        )).as_xml()

        job = Job.from_xml('matrix', xml)
        assert {'val1', 'val2'} == set(job.config['axis']['AXIS1'])

        new = Job.factory('matrix', config=dict(
            node='slave-ng',
            axis=dict(AXIS1=['val2', 'val3']),
        ))
        new = new.merge(job)

        assert {'val1', 'val2', 'val3'} == set(new.config['axis']['AXIS1'])
        assert {'slave-legacy', 'slave-ng'} == set(new.config['merged_nodes'])

    def test_parse_parameters(self):
        from jenkins_yml import Job

        xml = Job(name='freestyle', config=dict(
            node='slave',
            parameters=dict(PARAM1='default1'),
        )).as_xml()

        job = Job.from_xml('freestyle', xml)
        assert 'default1' == job.config['parameters']['PARAM1']

        new = Job.factory('freestyle', config=dict(
            parameters=dict(PARAM2='default2'),
        ))
        new = new.merge(job)
        assert 'default1' == new.config['parameters']['PARAM1']
        assert 'default2' == new.config['parameters']['PARAM2']
        assert 'NODE' not in new.config['parameters']
        assert 'REVISION' not in new.config['parameters']
