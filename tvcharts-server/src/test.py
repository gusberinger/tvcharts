from server import app
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

    # tt0025509 has no votes on each episode
    # make sure not in search database
    def test_search(self):
        tester = app.test_client(self)
        response = tester.get("/search/", content_type = "html/text")
        self.assertEqual(response.status_code, 200)
        search_db = response.get_json()
        tconst_list = [entry["tconst"] for entry in search_db]
        self.assertNotIn("tt0025509", tconst_list)


if __name__ == "__main__":
    unittest.main()
