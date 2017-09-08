import json
import unittest
from pprint import pprint

import httpretty

from eve_embedded.embedded import clean_embedded_item
from tests import TestBase  # noqa: E402


class TestEveEmbedded(TestBase):

    @httpretty.activate
    def test_embedded_rest_relation(self):
        httpretty.disable()

        peter_uri = '/people/585a8be8f0983235bf0f95ed'
        people = self.parse_response(self.test_client.get(peter_uri))
        expected = people.copy()

        skills_uri = '/skills?where={"_id":{"$in":["570c24f8de9f0c5e6c7a2e71","570c24fbde9f0c5e6c7a2e9f"]}}'
        httpretty.enable()
        skills = self.parse_response(self.test_client.get(
            skills_uri
        ))

        httpretty.register_uri(httpretty.GET,
                               'http://localhost:8080' + skills_uri,
                               content_type="application/json",
                               body=json.dumps(skills))

        embedded_skills = [clean_embedded_item(skill) for skill in skills["_items"]]
        expected["rest_skills"] = embedded_skills

        peter_rest_skills = '/people/585a8be8f0983235bf0f95ed?embedded={"rest_skills":1}'
        people = self.parse_response(self.test_client.get(peter_rest_skills))
        self.assertEqual(expected, people)

    @unittest.skip
    @httpretty.activate
    def test_embedded_rest_relation_nested(self):
        httpretty.disable()

        programmer_uri = '/roles/59b21c8ace035320ac129551'
        roles = self.parse_response(self.test_client.get(programmer_uri))
        expected = roles.copy()

        skills_uri = '/skills?where={"_id":{"$in":["570c24f8de9f0c5e6c7a2e71","570c24fbde9f0c5e6c7a2e9f"]}}'
        skills = self.parse_response(self.test_client.get(
            skills_uri
        ))
        embedded_skills = [clean_embedded_item(skill) for skill in skills["_items"]]
        # expected["rest_skills"] = embedded_skills

        peter_uri = '/people?where={"_id":{"$in":["585a8be8f0983235bf0f95ed"]}}'
        people = self.parse_response(self.test_client.get(peter_uri))

        cleaned_embedded_people = clean_embedded_item(people["_items"][0])
        cleaned_embedded_people["rest_skills"] = embedded_skills
        expected["rest_people"] = [cleaned_embedded_people]

        httpretty.enable()
        httpretty.register_uri(httpretty.GET,
                               'http://localhost:8080' + skills_uri,
                               content_type="application/json",
                               body=json.dumps(skills))

        httpretty.register_uri(httpretty.GET,
                               'http://localhost:8080' + peter_uri,
                               content_type="application/json",
                               body=json.dumps(people))

        programmer_rest_uri = '/roles/59b21c8ace035320ac129551?embedded={"rest_people":1,"rest_people.rest_skills":1}'
        roles = self.parse_response(self.test_client.get(programmer_rest_uri))
        self.assertEqual(expected, roles)

    @unittest.skip
    # def notest_doc_is_dict(self):
    def test_embedded_relations(self):
        doc = self.test_client \
            .get('/people?embedded={"relations.relation":1}') \
            .get_data() \
            .decode('utf-8')

        # self.assertEqual(doc.status_code, 200)

        j = json.loads(doc)
        print("--ls--" * 10)
        pprint(j)
        self.assertIn('_items', doc)
        # self.assertIsInstance(doc, dict)

    @httpretty.activate
    @unittest.skip
    def test_embedded_rest_relations(self):
        httpretty.disable()

        expected = self.test_client \
            .get('/people') \
            .get_data() \
            .decode('utf-8')
        expected_json = json.loads(expected)
        pprint(expected_json)

        httpretty.enable()
        import re
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://myapi.com/(.*)"),
            body="{}",
        )
        httpretty.register_uri(httpretty.GET,
                               'http://myapi.com/people?embedded={"rest_relations.relation":1}',
                               content_type="application/json",
                               body=expected)
        print("register http://myapi.com/people/54f112defba522406c9cc209",
              type(json.dumps(expected_json.get('_items')[0])))
        httpretty.register_uri(httpretty.GET,
                               'http://myapi.com/people/54f112defba522406c9cc209',
                               content_type="application/json",
                               body=json.dumps(expected_json.get('_items')[0]))
        httpretty.register_uri(httpretty.GET,
                               'http://myapi.com/people/585a8be8f0983235bf0f95ed',
                               content_type="application/json",
                               body=json.dumps(expected_json.get('_items')[1]))

        doc = self.test_client \
            .get('/people?embedded={"rest_relations.relation":1}') \
            .get_data() \
            .decode('utf-8')

        print(">>> last_request")
        pprint(httpretty.last_request().body)
        print("<<< last_request")

        response_json = json.loads(doc)
        print("--mocked--" * 10)
        pprint(response_json)

        self.assertIn('_items', doc)
        self.assertEqual(expected_json, response_json)
        # self.assertIsInstance(doc, dict)

        # httpretty.disable()
        # httpretty.reset()


if __name__ == '__main__':
    unittest.main()
