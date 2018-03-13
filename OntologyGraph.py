#
# Copyright 2012-2013 Ontology Engineering Group, Universidad Politecnica de Madrid, Spain
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# @author Ahmad Alobaid
#

import rdflib


class OntologyGraph(object):

    def __init__(self, ontology_dir):
        g = rdflib.Graph()
        g.load(ontology_dir)
        self.g = g
        self.title = ''
        self.uri = ''
        self.version = ''

    def get_title(self):
        titles = list(self.g[:rdflib.term.URIRef(u'http://purl.org/dc/elements/1.1/title')])
        if len(titles) > 0:
            return str(titles[0][1])
        return ''

    def get_uri(self):
        uris = list(self.g[:rdflib.term.URIRef(u'http://purl.org/vocab/vann/preferredNamespaceUri')])
        if len(uris) > 0:
            return str(uris[0][0])
        return ''

    def get_version(self):
        versions = list(self.g[:rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#versionInfo')])
        if len(versions) > 0:
            return str(versions[0][1])
        return ''
