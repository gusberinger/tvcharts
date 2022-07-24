from tqdm import tqdm
from server import app, search
import unittest

class FlaskTestCase(unittest.TestCase):

    def test_sopranos(self):
        tester = app.test_client(self)
        response = tester.get("/episodes/tt0141842", content_type = "html/text")
        self.assertEqual(response.status_code, 200)

    def test_specials(self):
        # tt0383126 - mythbusters
        # make sure specials with no season are not included
        tester = app.test_client(self)
        response = tester.get("/episodes/tt0383126", content_type = "html/text")
        self.assertEqual(response.status_code, 200)

    def test_poster_sopranos(self):
        tester = app.test_client(self)
        response = tester.get("/poster/tt0141842", content_type = "image/jpeg")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    print(search)
    unittest.main()
