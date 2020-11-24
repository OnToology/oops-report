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
import traceback
import os
import xml.etree.ElementTree as ET

# import rdfxml
import argparse
import requests
from OntologyGraph import OntologyGraph


def get_oops_pitfalls(ontology_dir):
    try:
        f = open(ontology_dir, 'r')
        ont_file_content = f.read()
    except:
        f = open(ontology_dir, 'r', encoding='utf-8')
        ont_file_content = f.read()
    url = "http://oops.linkeddata.es/rest"
    xml_content = """
    <?xml version="1.0" encoding="UTF-8"?>
    <OOPSRequest>
          <OntologyUrl></OntologyUrl>
          <OntologyContent>%s</OntologyContent>
          <Pitfalls>2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 19, 20, 21, 22, 24, 25, 25, 26, 27, 28, 29</Pitfalls>
          <OutputFormat>RDF/XML</OutputFormat>
    </OOPSRequest>
    """ % (ont_file_content)
    headers = {'Content-Type': 'application/xml',
               'Connection': 'Keep-Alive',
               'Content-Length': str(len(xml_content)),
               'Accept-Charset': 'utf-8'
               }
    oops_reply = requests.post(url, data=xml_content.encode('utf-8'), headers=headers)
    oops_reply = oops_reply.text
    # print("oops_reply: ")
    # print(oops_reply)
    # print oops_reply
    if 'http://www.oeg-upm.net/oops/unexpected_error' in oops_reply:
        raise Exception("unexpected error in OOPS webservice")
    if oops_reply[:50] == '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">':
        if '<title>502 Proxy Error</title>' in oops_reply:
            raise Exception('Ontology is too big for OOPS')
        else:
            raise Exception('Generic error from OOPS')
    pitfalls = parse_oops_issues(oops_reply)
    return pitfalls


def create_report(pitfalls, ontology_dir):
    ont_graph = OntologyGraph(ontology_dir)
    panels = []
    for i, p in enumerate(pitfalls):
        p["id"] = i
        panel = get_panel(p)
        panels.append(panel)
    base_dir = os.path.dirname(os.path.realpath(__file__))
    print("base_dir: %s" % base_dir)
    try:
        f = open(os.path.join(base_dir, "report.html"))
        html = f.read()
    except:
        f = open(os.path.join(base_dir, "report.html"), encoding='utf-8')
        html = f.read()
    report = html % (
        ont_graph.get_uri(), ont_graph.get_title(), ont_graph.get_uri(), ont_graph.get_title(), ont_graph.get_uri(),
        ont_graph.get_uri(), ont_graph.get_version(), "".join(panels))
    return report


def save_report(report, ontology_dir, output_dir):
    # maybe we can add some kind of options of the output file name
    # file_name = ontology_dir.split(os.sep)[-1]
    # file_name+= ".html"
    file_name = "oops.html"
    print("output filename: %s" % file_name)
    print("output dir: %s" % output_dir)
    try:
        f = open(os.path.join(output_dir, file_name), 'w')
        f.write(report)
    except:
        f = open(os.path.join(output_dir, file_name), 'w', encoding='utf-8')
        f.write(report)
    f.close()


def parse_oops_issues(oops_rdf):
    """
    To parse the oops_rdf response
    :param oops_rdf: rdfxml OOPS! reply
    :return: list of pitalls, each as a dict
    """
    root = ET.fromstring(oops_rdf)
    pitfalls = []
    for child in root:
        pitf = get_desc(child)
        if pitf is not None:
            pitfalls.append(pitf)
    return pitfalls


def get_desc(desc_xml):
    """
    From XML child to dict
    :param desc_xml:
    :return:
    """
    has_code = ""
    has_name = ""
    has_desc = ""
    has_importance = ""
    has_num_aff = ""
    affected_elements = []
    for att in desc_xml:
        if att.tag == '{http://oops.linkeddata.es/def#}hasAffectedElement':
            affected_elements.append(att.text)
        elif att.tag == '{http://oops.linkeddata.es/def#}hasImportanceLevel':
            has_importance = att.text
        elif att.tag == '{http://oops.linkeddata.es/def#}hasName':
            has_name = att.text
        elif att.tag == '{http://oops.linkeddata.es/def#}hasNumberAffectedElements':
            has_num_aff = att.text
        elif att.tag == '{http://oops.linkeddata.es/def#}hasDescription':
            has_desc = att.text
        elif att.tag == '{http://oops.linkeddata.es/def#}hasCode':
            has_code = att.text
    desc = {
        'code': has_code,
        'name': has_name,
        'description': has_desc,
        'importance': has_importance,
        'num_of_affected_elements': has_num_aff,
        'affected_elements': affected_elements
    }
    if has_code == '':
        return None
    return desc


def get_panel(pitfall):
    """
    :param pitfall: as a dict
    :return: html of a single pitfall
    """
    # print("In get panel")
    labels = {
        "Minor": "label-minor",
        "Important": "label-warning",
        "Critical": "label-danger"
    }
    # print("pitfall: ")
    # print(pitfall)
    label_key = pitfall["importance"]
    # label_key = str(pitfall["importance"]).replace('"','')
    return """
    <div class="panel panel-default">
    <div class="panel-heading">
    <h4 class="panel-title">
    <a data-toggle="collapse" href="#collapse%d">
    %s. %s<span style="float: right;">%s cases detected. <span class="label %s">%s</span></span></a>
    </h4>
    </div>
    <div id="collapse%d" class="panel-collapse collapse">
    <div class="panel-body">
    <p>%s</p>
    </div>
    </div>
    </div>
    """ % (pitfall["id"], pitfall["code"], pitfall["name"], pitfall["num_of_affected_elements"],
           labels[label_key], pitfall["importance"], pitfall["id"], pitfall["description"])


def workflow(output_dir, ontology_dir):
    pitfalls = get_oops_pitfalls(ontology_dir=ontology_dir)
    report = create_report(pitfalls, ontology_dir)
    save_report(report=report, output_dir=output_dir, ontology_dir=ontology_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a nice HTML from')
    parser.add_argument('--outputdir', help='the output directory')
    parser.add_argument('--ontologydir', help='the local directory to the ontology')
    args = parser.parse_args()
    try:
        workflow(output_dir=args.outputdir, ontology_dir=args.ontologydir)
        print("report is generated successfully")
    except Exception as e:
        print("exception in generating oops error: %s" % str(e))
        #traceback.print_exc()