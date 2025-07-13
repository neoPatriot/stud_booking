from django.test import TestCase
from .models import Studio, Room


class StudioModelTest(TestCase):
    def setUp(self):
        self.studio = Studio.objects.create(
            name="Test Studio",
            contact_phone="+79998887766",
            contact_email="test@studio.com"
        )

    def test_studio_creation(self):
        self.assertEqual(self.studio.name, "Test Studio")
        self.assertEqual(str(self.studio), "Test Studio")


class RoomModelTest(TestCase):
    def setUp(self):
        self.studio = Studio.objects.create(
            name="Test Studio",
            contact_phone="+79998887766",
            contact_email="test@studio.com"
        )
        self.room = Room.objects.create(
            studio=self.studio,
            name="Drum Room",
            slot_duration=120,
            area=40
        )

    def test_room_creation(self):
        self.assertEqual(self.room.name, "Drum Room")
        self.assertEqual(self.room.slot_duration, 120)
        self.assertEqual(str(self.room), "Drum Room (Test Studio)")
