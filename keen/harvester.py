from datetime import datetime
import json
import os

import keen
from pystackalytics import Stackalytics
import pytz
import requests

# This URL tracks contributor stats, including name, id,
# and total additions/deletions/commits
HELM_CONTRIBUTORS_URL = 'https://api.github.com/repos/openstack/openstack-helm/stats/contributors'
KOLLA_CONTRIBUTORS_URL = 'https://api.github.com/repos/openstack/kolla-kubernetes/stats/contributors'
FUELCCP_CONTRIBUTORS_URL = 'https://api.github.com/repos/openstack/fuel-ccp/stats/contributors'

# This URL tracks stargazer information, including the
# name of those who have starred the repository
HELM_STARGAZER_URL = 'https://api.github.com/repos/openstack/openstack-helm/stargazers'
KOLLA_STARGAZER_URL = 'https://api.github.com/repos/openstack/kolla-kubernetes/stargazers'
FUELCCP_STARGAZER_URL = 'https://api.github.com/repos/openstack/fuel-ccp/stargazers'

HELM_FORK_URL = 'https://api.github.com/repos/openstack/openstack-helm/forks'
KOLLA_FORK_URL = 'https://api.github.com/repos/openstack/kolla-kubernetes/forks'
FUELCCP_FORK_URL = 'https://api.github.com/repos/openstack/fuel-ccp/forks'

HELM_COMMITS_URL = 'https://api.github.com/repos/openstack/openstack-helm/commits'
KOLLA_COMMITS_URL = 'https://api.github.com/repos/openstack/kolla-kubernetes/commits'
FUELCCP_COMMITS_URL = 'https://api.github.com/repos/openstack/fuel-ccp/commits'

# The following keen values are pulled in from env vars
keen.project_id = os.environ['KEEN_PROJECT_ID']
keen.write_key = os.environ['KEEN_WRITE_KEY']
keen.read_key = os.environ['KEEN_READ_KEY']
keen.master_key = os.environ['KEEN_MASTER_KEY']

# Create map of all contributors and their overlords
contributors = {"alanmeadows":"AT&T",
                "v1k0d3n":"AT&T",
                "intlabs":"Independent",
                "larryrensing":"AT&T",
                "DTadrzak":"Intel",
                "wilkers-steve":"AT&T",
                "PiotrProkop":"Intel",
                "wilreichert":"SK Telecom",
                "galthaus":"Digital Rebar",
                "rmjozsa":"Independent",
                "mattmceuen":"AT&T",
                "mm9745":"AT&T",
                "gardlt":"AT&T",
                "korroot":"Intel",
                "laplague":"Independent",
                "stannum-l":"Accenture",
                "alraddarla":"AT&T",
                "maris-accenture":"Accenture",
                "Ciello89":"AT&T",
                "ss7pro":"AT&T",
                "dulek":"Intel",
                "rwellum":"Lenovo",
                "jaugustine":"AT&T",
                "mark-burnett":"Independent",
                "srwilkers":"AT&T"}


def fork_affiliations(event_name, response, contributors):
    for r in response:
        fork_created = r['created_at']
        owner = r['owner']['login']
        if owner in contributors:
            keen.add_event(event_name,
                {
                    "keen": {
                        "timestamp": fork_created
                    },
                    "payload": r,
                    "affiliation": contributors.get(owner)
            })
        else:
            keen.add_event(event_name,
                {
                    "keen": {
                        "timestamp": fork_created
                    },
                    "payload": r
            })
    return

def commit_affiliations(event_name, response, contributors):
    for r in response:
        author = r['committer']
        if author is not None:
            name = author['login']
            if name in contributors:
                keen.add_event(event_name,
                    {
                        "payload": r,
                        "affiliation": contributors.get(name)
                    })
            else:
                keen.add_event(event_name, r)
    return


def additions_over_time_event(event_name, response):
    tz = pytz.timezone('America/Chicago')
    for r in response.json():
        for w in r['weeks']:
            timestamp = datetime.fromtimestamp(w['w'], tz).isoformat()
            keen.add_event(event_name, {
                "keen": {
                    "timestamp": timestamp
                },
                "author": r['author']['login'],
                "payload": w,
                "affiliation": contributors.get(r['author']['login'])
            })
    return

def stackalytics_corporate_contributors(event_name, p_type, mod, met):
    ACTIVITY_URL = 'http://stackalytics.com/api/1.0/stats/companies'
    payload = {'project_type':p_type,'module':mod,'metric':met}
    response = requests.get(ACTIVITY_URL, params=payload)
    if response.json() is None:
        return
    for r in response.json()['stats']:
        keen.add_event(event_name, r)
    return

def stackalytics_engineers(event_name, p_type, mod, met):
    ACTIVITY_URL = 'http://stackalytics.com/api/1.0/stats/engineers'
    payload = {'project_type':p_type,'module':mod,'metric':met}
    response = requests.get(ACTIVITY_URL, params=payload)
    if response.json() is None:
        return
    for r in response.json()['stats']:
        keen.add_event(event_name, r)
    return

def main():

    contributors = {"alanmeadows":"AT&T",
                    "v1k0d3n":"AT&T",
                    "intlabs":"Independent",
                    "larryrensing":"AT&T",
                    "DTadrzak":"Intel",
                    "wilkers-steve":"AT&T",
                    "PiotrProkop":"Intel",
                    "wilreichert":"SK Telecom",
                    "galthaus":"Digital Rebar",
                    "rmjozsa":"Independent",
                    "mattmceuen":"AT&T",
                    "mm9745":"AT&T",
                    "gardlt":"AT&T",
                    "korroot":"Intel",
                    "laplague":"Independent",
                    "stannum-l":"Accenture",
                    "alraddarla":"AT&T",
                    "maris-accenture":"Accenture",
                    "Ciello89":"AT&T",
                    "ss7pro":"AT&T",
                    "dulek":"Intel",
                    "rwellum":"Lenovo",
                    "jaugustine":"AT&T",
                    "mark-burnett":"Independent",
                    "srwilkers":"AT&T"}

    # Send all contributor information to Keen
    helm_contrib_response = requests.get(HELM_CONTRIBUTORS_URL)
    kolla_contrib_response = requests.get(KOLLA_CONTRIBUTORS_URL)
    fuelccp_contrib_response = requests.get(FUELCCP_CONTRIBUTORS_URL)

    #headers = {'Accept': 'application/vnd.github.v3.star+json'}
    #helm_stargaze_response = requests.get(HELM_STARGAZER_URL, headers=headers)
    #kolla_stargaze_response = requests.get(KOLLA_STARGAZER_URL, headers=headers)
    #fuelccp_stargaze_response = requests.get(FUELCCP_STARGAZER_URL, headers=headers)

    #helm_fork_response = requests.get(HELM_FORK_URL).json()
    #kolla_fork_response = requests.get(KOLLA_FORK_URL).json()
    #fuelccp_fork_response = requests.get(FUELCCP_FORK_URL).json()

    #helm_commit_response = requests.get(HELM_COMMITS_URL).json()
    #print json.dumps(helm_commit_response)
    #kolla_commit_response = requests.get(KOLLA_COMMITS_URL).json()
    #fuelccp_commit_response = requests.get(FUELCCP_COMMITS_URL).json()

    #commit_affiliations("OpenStack_Helm_Commits", helm_commit_response, contributors)
    #commit_affiliations("Kolla_Kubernetes_Commits", kolla_commit_response, contributors)
    #commit_affiliations("Fuel_CCP_Commits", fuelccp_commit_response, contributors)

    #fork_affiliations("OpenStack_Helm_Forks", helm_fork_response, contributors)
    #fork_affiliations("Kolla_Kubernetes_Forks", kolla_fork_response, contributors)
    #fork_affiliations("Fuel_CCP_Forks", fuelccp_fork_response, contributors)

    #for helm_commit in helm_commit_response.json():
    #    keen.add_event("OpenStack_Helm_Commits", helm_commit)

    #for kolla_commit in kolla_commit_response.json():
    #    keen.add_event("Kolla_Kubernetes_Commits", kolla_commit)

    #for fuel_commit in fuelccp_commit_response.json():
    #    keen.add_event("Fuel_CCP_Commits", fuel_commit)

    #for helm_contrib in helm_contrib_response.json():
    #    keen.add_event("OpenStack_Helm_Contributors", helm_contrib)

    #for kolla_contrib in kolla_contrib_response.json():
    #    keen.add_event("Kolla_Kubernetes_Contributors", kolla_contrib)

    #for fuelccp_contrib in fuelccp_contrib_response.json():
    #    keen.add_event("Fuel_CCP_Contributors", fuelccp_contrib)

    #for helm_response in helm_stargaze_response.json():
    #    starred = helm_response['starred_at']
    #    keen.add_event("OpenStack_Helm_Stargazers",
    #    {
    #        "keen": {
    #        "timestamp": starred
    #        },
    #        "payload": helm_response
    #    })

    #for kolla_response in kolla_stargaze_response.json():
    #    kolla_starred = kolla_response['starred_at']
    #    keen.add_event("Kolla_Kubernetes_Stargazers",
    #        {
    #            "keen": {
    #                "timestamp": kolla_starred
    #            },
    #            "payload": kolla_response
    #        })

    #for fuelccp_response in fuelccp_stargaze_response.json():
    #    fuel_starred = fuelccp_response['starred_at']
    #    keen.add_event("Fuel_CCP_Stargazers",
    #        {
    #            "keen": {
    #                "timestamp": fuel_starred
    #            },
    #            "payload": fuelccp_response
    #        })

    #additions_over_time_event("OpenStack-Helm_Additions", helm_contrib_response)
    #additions_over_time_event("FuelCCP_Additions", fuelccp_contrib_response)
    #additions_over_time_event("Kolla_Kubernetes_Additions", kolla_contrib_response)

    stackalytics_corporate_contributors("OSH_commits", 'openstack-others', 'openstack-helm', 'commits')
    stackalytics_corporate_contributors("OSH_marks", 'openstack-others', 'openstack-helm', 'marks')
    stackalytics_corporate_contributors("OSH_bpd", 'openstack-others', 'openstack-helm', 'bpd')
    stackalytics_corporate_contributors("OSH_patches", 'openstack-others', 'openstack-helm', 'patches')

    stackalytics_engineers("engineers_commits", 'openstack-others', 'openstack-helm', 'commits')
    stackalytics_engineers("engineers_marks", 'openstack-others', 'openstack-helm', 'marks')
    stackalytics_engineers("engineers_bpd", 'openstack-others', 'openstack-helm', 'bpd')
    stackalytics_engineers("engineers_patches", 'openstack-others', 'openstack-helm', 'patches')



    return

if __name__ == "__main__":
    main()

def additions_over_time_event(event_name, response):
    tz = pytz.timezone('America/Chicago')
    for r in response.json():
        for w in r['weeks']:
            timestamp = datetime.fromtimestamp(w['w'], tz).isoformat()
            keen.add_event(event_name, {
                "keen": {
                    "timestamp": timestamp
                },
                "author": r['author']['login'],
                "payload": w,
                "affiliation": contributors.get(r['author']['login'])
            })
    return


def add_keen_custom_timestamp(event_name, timestamp, payload):
    keen.add_event(event_name,
        {
            "keen": {
                "timestamp": timestamp
            },
            "payload": payload
        }
    )
    return

def keen_custom_event(event_name, url, headers, time_field):
    response = requests.get(url, headers=headers)
    for r in response.json():
        timestamp = r[time_field]
        add_keen_custom_timestamp(event_name, timestamp, r)
    return

def process_keen_event(event_name, url):
    response = requests.get(url)
    for r in response.json():
        keen.add_event(event_name, r)
    return
