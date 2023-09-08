"""ChoiceSet classes for device onboarding."""

from nautobot.core.choices import ChoiceSet
from nautobot.dcim.models import DeviceType


class OnboardingStatusChoices(ChoiceSet):
    """Valid values for OnboardingTask "status"."""

    STATUS_FAILED = "failed"
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_SKIPPED = "skipped"

    CHOICES = (
        (STATUS_FAILED, "failed"),
        (STATUS_PENDING, "pending"),
        (STATUS_RUNNING, "running"),
        (STATUS_SUCCEEDED, "succeeded"),
        (STATUS_SKIPPED, "skipped"),
    )


class OnboardingFailChoices(ChoiceSet):
    """Valid values for OnboardingTask "failed reason"."""

    FAIL_LOGIN = "fail-login"
    FAIL_CONFIG = "fail-config"
    FAIL_CONNECT = "fail-connect"
    FAIL_EXECUTE = "fail-execute"
    FAIL_GENERAL = "fail-general"
    FAIL_DNS = "fail-dns"

    CHOICES = (
        (FAIL_LOGIN, "fail-login"),
        (FAIL_CONFIG, "fail-config"),
        (FAIL_CONNECT, "fail-connect"),
        (FAIL_EXECUTE, "fail-execute"),
        (FAIL_GENERAL, "fail-general"),
        (FAIL_DNS, "fail-dns"),
    )

def DeviceTypeChoiceGenerator():
    device_types = DeviceType.objects.all()
    CHOICES = (("", "---------"), *((dt.model, dt.model) for dt in device_types))
    return CHOICES