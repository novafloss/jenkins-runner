from unittest import TestCase


class TestFreestyle(TestCase):
    def test_no_params(self):
        from jenkins_yml.parser import Job

        xml = Job('freestyle').as_xml()

        assert '<project>' in xml
        assert 'jenkins-yml-runner' in xml

    def test_with_defaults(self):
        from jenkins_yml.parser import Job

        xml = Job(name='freestyle', params=dict(
            github_repository='https://github.com/owner/repository',
            scm_credentials='github-https',
            node='slave1',
        )).as_xml()

        assert 'github-https' in xml
        assert 'owner/repository.git' in xml
        assert '${REVISION}' in xml
        assert 'slave1' in xml


class TestMatrix(TestCase):
    def test_defaults(self):
        from jenkins_yml.parser import Job

        xml = Job(name='freestyle', params=dict(
            axis=dict(
                AXIS1=['val1', 'val2'],
            ),
            node='slave1',
        )).as_xml()

        assert 'jenkins-yml-runner' in xml
        assert 'test command' not in xml
        assert 'AXIS1' in xml
        assert 'master' in xml

    def test_axis_union(self):
        from jenkins_yml.parser import Job

        master_xml = Job(name='freestyle', params=dict(
            axis=dict(
                AXIS1=['val1', 'val2'],
            ),
            node='slave1',
        )).as_xml()

        branch_xml = Job(name='freestyle', params=dict(
            axis=dict(
                AXIS1=['val2', 'val3'],
            ),
            node='slave1',
        )).as_xml(current_xml=master_xml)

        assert 'val1' in branch_xml
        assert 'val3' in branch_xml
