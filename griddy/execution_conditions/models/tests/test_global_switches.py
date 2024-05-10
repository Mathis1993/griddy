import pytest
from django.contrib.contenttypes.models import ContentType
from execution_conditions.models import ExecutionCondition
from execution_conditions.tests.factories import DummySwitchFactory, ExecutionConditionFactory


@pytest.fixture()
def user_with_dummy_switch(user):
    def inner(switch_value=True):
        dummy_switch = DummySwitchFactory.create(value=switch_value)
        ExecutionConditionFactory.create(user=user, specific_condition=dummy_switch)
        return dummy_switch

    return inner


@pytest.mark.django_db()
def test_registering_dummy_switch_as_execution_condition(user):
    dummy_switch = DummySwitchFactory.create()

    # use factory
    execution_condition_1 = ExecutionConditionFactory.create(
        user=user, specific_condition=dummy_switch
    )
    assert execution_condition_1.content_object == dummy_switch

    # use model manager
    execution_condition_2 = ExecutionCondition.objects.create(
        name="my_execution_condition",
        user=user,
        content_type=ContentType.objects.get_for_model(dummy_switch),
        object_id=dummy_switch.id,
    )
    assert execution_condition_2.content_object == dummy_switch


@pytest.mark.django_db()
def test_execution_condition_generic_relation(user):
    dummy_switch = DummySwitchFactory.create()
    execution_condition = ExecutionConditionFactory.create(
        user=user, specific_condition=dummy_switch
    )

    assert dummy_switch.generic_execution_conditions.first() == execution_condition


@pytest.mark.django_db()
def test_execution_condition_is_satisfied(user_with_dummy_switch):
    dummy_switch = user_with_dummy_switch(switch_value=False)

    assert dummy_switch.is_satisfied() is False

    dummy_switch.value = True
    dummy_switch.save()

    assert dummy_switch.is_satisfied() is True
