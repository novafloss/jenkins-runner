from unittest import TestCase


class TestFreestyle(TestCase):
    def test_defaults(self):
        from jenkins_yml import Job

        xml = Job('freestyle').as_xml()

        assert '<project>' in xml
        assert 'jenkins-yml-runner' in xml
        assert 'YML_NOTIFY_URL' in xml

    def test_with_config(self):
        from jenkins_yml import Job

        config = dict(
            disabled=True,
            github_repository='https://github.com/owner/repository',
            scm_credentials='github-https',
            node='slave1',
            parameters=dict(
                PARAM1='default1',
            ),
            after_script=': teardown'
        )
        xml = Job(name='freestyle', config=config).as_xml()

        assert '<disabled>true</disabled>' in xml
        assert 'github-https' in xml
        assert 'owner/repository.git' in xml
        assert '${REVISION}' in xml
        assert '>NODE<' in xml
        assert 'slave1' in xml
        assert 'PARAM1' in xml
        assert 'default1' in xml
        assert 'TimerTrigger' not in xml
        assert 'after_script' in xml
        assert ': teardown' not in xml
        assert 'projectUrl>https://github' in xml
        assert 'refs/pull/*' in xml

        config['periodic'] = 'H 0 * * *'
        xml = Job(name='freestyle', config=config).as_xml()

        assert 'TimerTrigger' in xml
        assert 'H 0 * * *' in xml


class TestMatrix(TestCase):
    def test_axis(self):
        from jenkins_yml import Job

        config = dict(
            axis=dict(AXIS1=['val1', 'val2']),
            node='slave1',
        )
        xml = Job(name='freestyle', config=config).as_xml()

        assert 'jenkins-yml-runner' in xml
        assert 'AXIS1' in xml
        assert 'val1' in xml
        assert 'val2' in xml
        assert 'master' in xml
        assert 'TimerTrigger' not in xml

        config['periodic'] = 'H 0 * * *'
        xml = Job(name='freestyle', config=config).as_xml()

        assert 'TimerTrigger' in xml
        assert 'H 0 * * *' in xml
