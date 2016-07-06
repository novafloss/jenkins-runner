from unittest import TestCase


class TestFreestyle(TestCase):
    def test_empty_defaults(self):
        from jenkins_yml.renderer import generate

        yml = """
freestyle: |
  test command
"""
        jobs = list(generate(yml))
        assert 1 == len(jobs)
        name, xml = jobs[0]
        assert 'freestyle' == name
        assert '<project>' in xml
        assert 'jenkins-yml-runner' in xml
        assert 'test command' not in xml

    def test_with_defaults(self):
        from jenkins_yml.renderer import generate

        yml = """
freestyle: |
  test command
"""
        defaults = dict(
            github_repository='https://github.com/owner/repository',
            scm_credentials='github-https',

        )
        jobs = list(generate(yml, defaults))
        assert 1 == len(jobs)
        name, xml = jobs[0]
        assert 'github-https' in xml
        assert 'owner/repository.git' in xml
        assert '${REVISION}' in xml
