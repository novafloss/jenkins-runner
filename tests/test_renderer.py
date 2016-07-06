from unittest import TestCase


class TestFreestyle(TestCase):
    def test_empty_defaults(self):
        from jenkins_yml.renderer import generate

        yml = "freestyle: test command"
        jobs = list(generate(yml))
        assert 1 == len(jobs)
        name, xml = jobs[0]
        assert 'freestyle' == name
        assert '<project>' in xml
        assert 'jenkins-yml-runner' in xml
        assert 'test command' not in xml

    def test_with_defaults(self):
        from jenkins_yml.renderer import generate

        yml = "freestyle: test command"
        defaults = dict(
            github_repository='https://github.com/owner/repository',
            scm_credentials='github-https',
            node='slave1',
        )
        jobs = list(generate(yml, defaults))
        assert 1 == len(jobs)
        name, xml = jobs[0]
        assert 'github-https' in xml
        assert 'owner/repository.git' in xml
        assert '${REVISION}' in xml
        assert 'slave1' in xml


class TestMatrix(TestCase):
    def test_defaults(self):
        from jenkins_yml.renderer import generate

        yml = """
matrix:
  axis:
    AXIS1: [val1, val2]
  script: |
    test command
"""
        jobs = list(generate(yml))
        assert 1 == len(jobs)
        name, xml = jobs[0]
        assert 'matrix' == name
        assert 'jenkins-yml-runner' in xml
        assert 'test command' not in xml
        assert 'AXIS1' in xml
        assert 'master' in xml

    def test_axis_union(self):
        from jenkins_yml.renderer import generate

        master_yml = """
matrix:
  axis:
    AXIS1: [val1, val2]
"""

        master_xml = list(generate(master_yml))[0][1]
        branch_yml = """
matrix:
  axis:
    AXIS1: [val2, val3]
"""

        branch_xml = list(
            generate(branch_yml, currents=dict(matrix=master_xml))
        )[0][1]

        assert 'val1' in branch_xml
        assert 'val3' in branch_xml
