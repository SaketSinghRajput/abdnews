import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient

from .models import AdvertisementBanner


MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AdvertisementTrackingTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = APIClient()
        self.banner = AdvertisementBanner.objects.create(
            title='Homepage sponsor',
            image=self._image_file(),
            link_url='https://example.com',
            position=AdvertisementBanner.Position.HOMEPAGE,
            is_active=True,
        )

    def _image_file(self):
        image_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
        Image.new('RGB', (600, 200), color='red').save(image_path)
        with open(image_path, 'rb') as image:
            return SimpleUploadedFile('ad.png', image.read(), content_type='image/png')

    def test_tracks_ad_impressions_and_clicks(self):
        impression_response = self.client.post(
            f'/api/ads/{self.banner.pk}/track/',
            {'action': 'impression'},
            format='json',
        )
        click_response = self.client.post(
            f'/api/ads/{self.banner.pk}/track/',
            {'action': 'click'},
            format='json',
        )

        self.banner.refresh_from_db()

        self.assertEqual(impression_response.status_code, 200)
        self.assertEqual(click_response.status_code, 200)
        self.assertEqual(self.banner.impressions, 1)
        self.assertEqual(self.banner.clicks, 1)

    def test_rejects_unknown_tracking_action(self):
        response = self.client.post(
            f'/api/ads/{self.banner.pk}/track/',
            {'action': 'view'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
