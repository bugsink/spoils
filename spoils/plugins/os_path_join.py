from bandit.core.test_properties import test_id, checks
import bandit


# when I picked B380, B325 was the highest taken number in the B3xx series (blacklisted function calls)
@test_id('B380')
@checks('Call')
def no_os_path_join(context):
    if context.call_function_name_qual == 'os.path.join':
        return bandit.Issue(
            severity=bandit.HIGH,
            confidence=bandit.MEDIUM,
            text="Avoid unvalidated use of os.path.join()"
        )
