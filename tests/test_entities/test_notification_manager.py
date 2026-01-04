"""
Unittests for notifications

These tests verify that the notification manager correctly manages subscribers
(attach, detach, and notify) and that concrete subscribers return the expected
messages when notified.

Author: Peyman Khodabandehlouei
Date: 04-12-2025
"""

from tests.conftest import get_agent_notification_subscriber


def test_attach_and_detach_notification_subscribers(
    get_notification_manager,
    get_customer_notification_subscriber,
    get_agent_notification_subscriber,
):
    # Attach notification subscriber to notification manager
    get_notification_manager.attach(get_customer_notification_subscriber)
    get_notification_manager.attach(get_agent_notification_subscriber)

    # Test number of subscribers
    assert len(get_notification_manager.subscribers) == 2
    assert get_customer_notification_subscriber in get_notification_manager.subscribers
    assert get_agent_notification_subscriber in get_notification_manager.subscribers

    # Detach agent subscriber
    get_notification_manager.detach(get_agent_notification_subscriber)
    assert get_agent_notification_subscriber not in get_notification_manager.subscribers
    assert get_customer_notification_subscriber in get_notification_manager.subscribers


def test_notify_calls_update_on_all_subscribers_with_mocker(
    get_notification_manager, mocker
):
    # Create mock subscribers
    sub1 = mocker.MagicMock()
    sub2 = mocker.MagicMock()

    # Attach notification subscriber to notification manager
    get_notification_manager.attach(sub1)
    get_notification_manager.attach(sub2)

    # Send notification to all subscribers
    get_notification_manager.notify()

    # each subscriber's update should be called exactly once
    sub1.update.assert_called_once_with(get_notification_manager)
    sub2.update.assert_called_once_with(get_notification_manager)


def test_customer_subscriber_update(
    get_notification_manager,
    get_customer_notification_subscriber,
):

    result = get_customer_notification_subscriber.update(get_notification_manager)

    assert result == "Notification sent to the customer"


def test_agent_subscriber_update(
    get_notification_manager, get_agent_notification_subscriber
):
    result = get_agent_notification_subscriber.update(get_notification_manager)

    assert result == "Notification sent to the agent"
