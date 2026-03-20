from django.test import TestCase
from datetime import date, timedelta
from holidays.models import Holiday
from holidays.services import HolidayService


class HolidayServiceTest(TestCase):

    def setUp(self):
        self.today = date.today()
        
        # Holiday 1: Upcoming next week
        self.upcoming = Holiday.objects.create(
            name="Upcoming Fest",
            date=self.today + timedelta(days=7),
            holiday_type='national'
        )
        # Holiday 2: Past (last week)
        self.past = Holiday.objects.create(
            name="Past Fest",
            date=self.today - timedelta(days=7),
            holiday_type='national'
        )
        # Holiday 3: Company type
        Holiday.objects.create(
            name="Founders Day",
            date=self.today + timedelta(days=14),
            holiday_type='company'
        )

    def test_get_for_year(self):
        # We assume setUp holidays fall in current year
        hols = HolidayService.get_for_year(self.today.year)
        self.assertEqual(hols.count(), 3)
        self.assertEqual(hols[0].year, self.today.year)

    def test_get_upcoming(self):
        # Should only return holidays >= today
        upcoming_hols = HolidayService.get_upcoming(limit=5)
        self.assertEqual(upcoming_hols.count(), 2)
        
        # Check ordering is correct (closest first)
        self.assertEqual(upcoming_hols[0].name, "Upcoming Fest")
        self.assertEqual(upcoming_hols[1].name, "Founders Day")

    def test_get_type_summary(self):
        # 2 national, 1 company created in setUp
        summary = HolidayService.get_type_summary(self.today.year)
        self.assertEqual(summary['national'], 2)
        self.assertEqual(summary['company'], 1)
        self.assertNotIn('regional', summary)

    def test_create_update_holiday(self):
        hol = HolidayService.create_holiday({
            'name': 'New Year',
            'date': date(2027, 1, 1),
            'holiday_type': 'national'
        })
        self.assertEqual(hol.year, 2027)

        updated = HolidayService.update_holiday(hol.pk, {'name': 'New Year Celebration'})
        self.assertEqual(updated.name, 'New Year Celebration')
        self.assertEqual(updated.year, 2027)
