"""Tests for the event bus."""

import unittest
from unittest.mock import Mock, call

from src.event.event import Event, OutputMessage
from src.event.event_bus import EventBus


class TestEventBus(unittest.TestCase):

    def setUp(self) -> None:
        self.event_bus = EventBus()

    def test_subscribe_handler(self) -> None:
        handler = Mock()

        self.event_bus.subscribe(handler)

        event = OutputMessage(
            command="test",
            message="Hello",
        )
        self.event_bus.publish(event)

        handler.assert_called_once_with(event)

    def test_publish_to_multiple_subscribers(self) -> None:
        first_handler = Mock()
        second_handler = Mock()
        event = OutputMessage(
            command="test",
            message="Hello",
        )

        self.event_bus.subscribe(first_handler)
        self.event_bus.subscribe(second_handler)

        self.event_bus.publish(event)

        first_handler.assert_called_once_with(event)
        second_handler.assert_called_once_with(event)

    def test_unsubscribe_handler(self) -> None:
        handler = Mock()
        event = OutputMessage(
            command="test",
            message="Hello",
        )

        self.event_bus.subscribe(handler)
        self.event_bus.unsubscribe(handler)
        self.event_bus.publish(event)

        handler.assert_not_called()

    def test_unsubscribe_one_handler_preserves_others(self) -> None:
        first_handler = Mock()
        second_handler = Mock()
        event = OutputMessage(
            command="test",
            message="Hello",
        )

        self.event_bus.subscribe(first_handler)
        self.event_bus.subscribe(second_handler)
        self.event_bus.unsubscribe(first_handler)

        self.event_bus.publish(event)

        first_handler.assert_not_called()
        second_handler.assert_called_once_with(event)

    def test_publish_without_subscribers(self) -> None:
        event = OutputMessage(
            command="test",
            message="Hello",
        )

        # Publishing without subscribers should not raise an exception.
        self.event_bus.publish(event)

    def test_publish_passes_same_event_to_all_handlers(self) -> None:
        first_handler = Mock()
        second_handler = Mock()
        event = OutputMessage(
            command="test",
            message="Hello",
        )

        self.event_bus.subscribe(first_handler)
        self.event_bus.subscribe(second_handler)

        self.event_bus.publish(event)

        first_received_event = first_handler.call_args.args[0]
        second_received_event = second_handler.call_args.args[0]

        self.assertIs(first_received_event, event)
        self.assertIs(second_received_event, event)

    def test_subscribing_same_handler_twice_calls_it_twice(self) -> None:
        handler = Mock()
        event = OutputMessage(
            command="test",
            message="Hello",
        )

        self.event_bus.subscribe(handler)
        self.event_bus.subscribe(handler)

        self.event_bus.publish(event)

        self.assertEqual(handler.call_count, 2)
        self.assertEqual(
            handler.call_args_list,
            [call(event), call(event)],
        )

    def test_publish_uses_snapshot_of_handlers(self) -> None:
        second_handler = Mock()
        event = OutputMessage(
            command="test",
            message="Hello",
        )

        def first_handler(received_event: Event) -> None:
            self.event_bus.unsubscribe(first_handler)

        self.event_bus.subscribe(first_handler)
        self.event_bus.subscribe(second_handler)

        # Unsubscribing during publication should not prevent the
        # second handler from receiving the current event.
        self.event_bus.publish(event)

        second_handler.assert_called_once_with(event)

        # The first handler was removed and should not receive later events.
        self.event_bus.publish(event)

        second_handler.assert_called_with(event)
        self.assertEqual(second_handler.call_count, 2)

    def test_unsubscribe_unknown_handler_raises_error(self) -> None:
        handler = Mock()

        with self.assertRaises(ValueError):
            self.event_bus.unsubscribe(handler)

