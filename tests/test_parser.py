from unittest import TestCase


class TestYml(TestCase):
    def test_empty_defaults(self):
        from jenkins_yml.parser import Job

        yml = "freestyle: test command"
        jobs = list(Job.parse_all(yml))
        assert 1 == len(jobs)
        job = jobs[0]
        assert 'freestyle' == job.name
        assert job.config

    def test_with_defaults(self):
        from jenkins_yml.parser import Job

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
