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

import argparse
import requests
import rdfxml


def get_oops_pitfalls(ontology_dir):
    f = open(ontology_dir, 'r')
    ont_file_content = f.read()
    url = 'http://oops-ws.oeg-upm.net/rest'
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
    oops_reply = requests.post(url, data=xml_content, headers=headers)
    oops_reply = oops_reply.text
    if oops_reply[:50] == '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">':
        if '<title>502 Proxy Error</title>' in oops_reply:
            raise Exception('Ontology is too big for OOPS')
        else:
            raise Exception('Generic error from OOPS')
    pitfalls = output_parsed_pitfalls(oops_reply)
    # for p in pitfalls:
    #     print "\n"
    #     for k in p.keys():
    #         print "%s: %s" % (str(k), str(p[k]))
    return pitfalls


def create_report(pitfalls):
    panels = []
    for i, p in enumerate(pitfalls):
        p["id"] = i
        panel = get_panel(p)
        panels.append(panel)
    f = open("report.html")
    html = f.read()
    html % ("title", "URI", "version", "".join(panels))
    f = open("new.html", "w")
    f.write(html % ("title", "URI", "version", "".join(panels)))
    f.close()


def parse_oops_issues(oops_rdf):
    p = rdfxml.parseRDF(oops_rdf)
    raw_oops_list = p.result
    oops_issues = {}

    # Filter #1
    # Construct combine all data of a single elements into one json like format
    for r in raw_oops_list:
        if r['domain'] not in oops_issues:
            oops_issues[r['domain']] = {}
        oops_issues[r['domain']][r['relation']] = r['range']

    # Filter #2
    # get rid of elements without issue id
    oops_issues_filter2 = {}
    for i in oops_issues:
        if '#' not in i:
            oops_issues_filter2[i] = oops_issues[i]

    # Filter #3
    # Only include actual issues (some data are useless to us)
    detailed_desc = []
    oops_issues_filter3 = {}
    for i in oops_issues_filter2:
        if '<http://www.oeg-upm.net/oops#hasNumberAffectedElements>' in oops_issues_filter2[i]:
            oops_issues_filter3[i] = oops_issues_filter2[i]

    # Filter #4
    # Only include data of interest about the issue
    oops_issues_filter4 = {}
    issue_interesting_data = [
        '<http://www.oeg-upm.net/oops#hasName>',
        '<http://www.oeg-upm.net/oops#hasCode>',
        '<http://www.oeg-upm.net/oops#hasDescription>',
        '<http://www.oeg-upm.net/oops#hasNumberAffectedElements>',
        '<http://www.oeg-upm.net/oops#hasImportanceLevel>',
        # '<http://www.oeg-upm.net/oops#hasAffectedElement>',
        '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
    ]
    for i in oops_issues_filter3:
        oops_issues_filter4[i] = {}
        for intda in issue_interesting_data:
            if intda in oops_issues_filter3[i]:
                oops_issues_filter4[i][intda] = oops_issues_filter3[i][intda]
    return oops_issues_filter4, issue_interesting_data


def output_parsed_pitfalls(oops_reply):
    issues, interesting_features = parse_oops_issues(oops_reply)
    pitfalls = []
    for i in issues:
        d = {}
        for intfea in interesting_features:
            if intfea in issues[i]:
                val = issues[i][intfea].split('^^')[0]
                key = intfea.split("#")[-1].replace('>', '')
                d[key] = val
        if d != {}:
            pitfalls.append(d)

    return pitfalls


def get_panel(pitfall):
    """
    :param pitfall: as a dict
    :return: html of a single pitfall
    """

    labels = {
        "Minor": "label-minor",
        "Important": "label-warning",
        "Critical": "label-danger"
    }
    label_key = str(pitfall["hasImportanceLevel"]).replace('"','')
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
    """ % (pitfall["id"], pitfall["hasCode"], pitfall["hasName"], pitfall["hasNumberAffectedElements"],
           labels[label_key], pitfall["hasImportanceLevel"], pitfall["id"], pitfall["hasDescription"])


def workflow(output_dir, ontology_dir):
    pitfalls = get_oops_pitfalls(ontology_dir=ontology_dir)
    report = create_report(pitfalls)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a nice HTML from')
    parser.add_argument('--outputdir', help='the output directory')
    parser.add_argument('--ontologydir', help='the local directory to the ontology')
    args = parser.parse_args()
    try:
        workflow(output_dir=args.outputdir, ontology_dir=args.ontologydir)
        print "report is generated successfully"
    except Exception as e:
        print "exception in generating oops error: %s" % str(e)
