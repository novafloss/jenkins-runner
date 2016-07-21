from unittest import TestCase


class TestFreestyle(TestCase):
    def test_defaults(self):
        from jenkins_yml import Job

        xml = Job('freestyle').as_xml()

        assert '<project>' in xml
        assert 'jenkins-yml-runner' in xml

    def test_with_config(self):
        from jenkins_yml import Job

        xml = Job(name='freestyle', config=dict(
            github_repository='https://github.com/owner/repository',
            scm_credentials='github-https',
            node='slave1',
            parameters=dict(
                PARAM1='default1',
            ),
            periodic='H 0 * * *',
        )).as_xml()

        assert 'github-https' in xml
        assert 'owner/repository.git' in xml
        assert '${REVISION}' in xml
        assert '>NODE<' in xml
        assert 'slave1' in xml
        assert 'PARAM1' in xml
        assert 'default1' in xml
        assert 'TimerTrigger' in xml
        assert 'H 0 * * *' in xml


class TestMatrix(TestCase):
    def test_axis(self):
        from jenkins_yml import Job

        xml = Job(name='freestyle', config=dict(
            axis=dict(AXIS1=['val1', 'val2']),
            node='slave1',
            periodic='H 0 * * *',
        )).as_xml()

        assert 'jenkins-yml-runner' in xml
        assert 'test command' not in xml
        assert 'AXIS1' in xml
        assert 'val1' in xml
        assert 'val2' in xml
        assert 'master' in xml
        assert 'TimerTrigger' in xml
        assert 'H 0 * * *' in xml
