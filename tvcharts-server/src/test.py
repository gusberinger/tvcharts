from tqdm import tqdm
from server import app, search
import unittest

class FlaskTestCase(unittest.TestCase):

    def test_sopranos(self):
        tester = app.test_client(self)
        response = tester.get("/tconst/tt0141842", content_type = "html/text")
        self.assertEqual(response.status_code, 200)

    def test_all(self):
        tconsts = [x[0] for x in search] 
        for tconst in tqdm(tconsts):
            tester = app.test_client(self)
            response = tester.get(f"/tconst/{tconst}", content_type = "html/text")
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    print(search)
    unittest.main()
