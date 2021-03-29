import unittest
import os
import requests
from main import *


if not os.path.exists('local'):
    os.makedirs('local')


class TestResponse(unittest.TestCase):
    """
    Test Generation of OOPS! report
    """

    def test_get_pitfalls(self):
        f = open("mock_response1.rdf")
        oops_reply = f.read()
        pitfalls = parse_oops_issues(oops_reply)
        f.close()
        self.assertEqual(len(pitfalls), 10)

    def test_alo(self):
        filename = "alo.owl"
        ont_path = os.path.join('local', filename)
        if not os.path.exists(ont_path):
            url = "https://raw.githubusercontent.com/ahmad88me/demo/master/alo.owl"
            r = requests.get(url, allow_redirects=True)
            f = open(ont_path, 'wb')
            f.write(r.content)
            f.close()
        out_html_path = "local/oops.html"
        if os.path.exists(out_html_path):
            os.remove(out_html_path)
        workflow("local", ont_path)
        self.assertTrue(os.path.exists(out_html_path))

    # def test_geo(self):
    #     filename = "geo.owl"
    #     ont_path = os.path.join('local', filename)
    #     if not os.path.exists(ont_path):
    #         url = "https://raw.githubusercontent.com/ahmad88me/demo/master/geolinkeddata.owl"
    #         r = requests.get(url, allow_redirects=True)
    #         f = open(ont_path, 'wb')
    #         f.write(r.content)
    #         f.close()
    #     out_html_path = "local/oops.html"
    #     if os.path.exists(out_html_path):
    #         os.remove(out_html_path)
    #     workflow("local", ont_path)
    #     self.assertTrue(os.path.exists(out_html_path))

    def test_qn(self):
        filename = "qn.owl"
        ont_path = os.path.join('local', filename)
        if not os.path.exists(ont_path):
            url = "https://raw.githubusercontent.com/ahmad88me/qs_onto/master/quran_ontology.owl"
            r = requests.get(url, allow_redirects=True)
            f = open(ont_path, 'wb')
            f.write(r.content)
            f.close()
        out_html_path = "local/oops.html"
        if os.path.exists(out_html_path):
            os.remove(out_html_path)
        workflow("local", ont_path)
        self.assertTrue(os.path.exists(out_html_path))


if __name__ == '__main__':
    unittest.main()
