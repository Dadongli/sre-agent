from django.test import Client, TestCase


class DashboardApiTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_dashboard_summary_shape(self) -> None:
        response = self.client.get('/api/dashboard/summary/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['cards']), 4)
        self.assertGreaterEqual(len(payload['timeline']), 5)
        self.assertIn('chatops_examples', payload)

    def test_runbook_sections(self) -> None:
        response = self.client.get('/api/agent/runbook/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('observability', payload)
        self.assertIn('chatops', payload)
