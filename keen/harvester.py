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
#KOLLA_CONTRIBUTORS_URL = 'https://api.github.com/repos/openstack/kolla-kubernetes/stats/contributors'
#FUELCCP_CONTRIBUTORS_URL = 'https://api.github.com/repos/openstack/fuel-ccp/stats/contributors'
ARMADA_CONTRIBUTORS_URL = 'https://api.github.com/repos/att-comdev/armada/stats/contributors'
DECKHAND_CONTRIBUTORS_URL = 'https://api.github.com/repos/att-comdev/deckhand/stats/contributors'
DRYDOCK_CONTRIBUTORS_URL = 'https://api.github.com/repos/att-comdev/drydock/stats/contributors'
SHIPYARD_CONTRIBUTORS_URL= 'https://api.github.com/repos/att-comdev/shipyard/stats/contributors'
PROMENADE_CONTRIBUTORS_URL= 'https://api.github.com/repos/att-comdev/promenade/stats/contributors'

# name of those who have starred the repository
HELM_STARGAZER_URL = 'https://api.github.com/repos/openstack/openstack-helm/stargazers'
#KOLLA_STARGAZER_URL = 'https://api.github.com/repos/openstack/kolla-kubernetes/stargazers'
#FUELCCP_STARGAZER_URL = 'https://api.github.com/repos/openstack/fuel-ccp/stargazers'
ARMADA_STARGAZER_URL = 'https://api.github.com/repos/att-comdev/armada/stargazers'
DECKHAND_STARGAZER_URL = 'https://api.github.com/repos/att-comdev/deckhand/stargazers'
DRYDOCK_STARGAZER_URL = 'https://api.github.com/repos/att-comdev/drydock/stargazers'
SHIPYARD_STARGAZER_URL= 'https://api.github.com/repos/att-comdev/shipyard/stargazers'
PROMENADE_STARGAZER_URL= 'https://api.github.com/repos/att-comdev/promenade/stargazers'

HELM_FORK_URL = 'https://api.github.com/repos/openstack/openstack-helm/forks'
#KOLLA_FORK_URL = 'https://api.github.com/repos/openstack/kolla-kubernetes/forks'
#FUELCCP_FORK_URL = 'https://api.github.com/repos/openstack/fuel-ccp/forks'
ARMADA_FORK_URL = 'https://api.github.com/repos/openstack/openstack-helm/forks'
DECKHAND_FORK_URL = 'https://api.github.com/repos/att-comdev/deckhand/forks'
DRYDOCK_FORK_URL = 'https://api.github.com/repos/att-comdev/drydock/forks'
SHIPYARD_FORK_URL = 'https://api.github.com/repos/att-comdev/shipyard/forks'
PROMENADE_FORK_URL = 'https://api.github.com/repos/att-comdev/promenade/forks'


HELM_COMMITS_URL = 'https://api.github.com/repos/openstack/openstack-helm/commits'
#KOLLA_COMMITS_URL = 'https://api.github.com/repos/openstack/kolla-kubernetes/commits'
#FUELCCP_COMMITS_URL = 'https://api.github.com/repos/openstack/fuel-ccp/commits'
ARMADA_COMMITS_URL = 'https://api.github.com/repos/att-comdev/armada/commits'
DECKHAND_COMMITS_URL = 'https://api.github.com/repos/att-comdev/deckhand/commits'
DRYDOCK_COMMITS_URL = 'https://api.github.com/repos/att-comdev/drydock/commits'
SHIPYARD_COMMITS_URL = 'https://api.github.com/repos/att-comdev/shipyard/commits'
PROMENADE_COMMITS_URL = 'https://api.github.com/repos/att-comdev/promenade/commits'

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
                "drewwalters96":"AT&T",
                "theyer":"AT&T",
                "g0r1v3r4":"AT&T",
                "alop":"Cisco",
                "fmontei":"AT&T",
                "sh8121att":"AT&T",
                "joedborg":"Canonical",
                "eanylin":"Ericsson",
                "jezogwza":"AT&T",
                "stannum-l":"Accenture",
                "alraddarla":"AT&T",
                "maris-accenture":"Accenture",
                "Ciello89":"AT&T",
                "ss7pro":"AT&T",
                "dulek":"Intel",
                "rwellum":"Lenovo",
                "jaugustine":"AT&T",
                "mark-burnett":"AT&T",
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
    for r in response.json():
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

def starred_data(event_name, response):
    for r in response.json():
        starred = r['starred_at']
        keen.add_event(event,
        {
           "keen": {
           "timestamp": starred
           },
           "payload": r
        })
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
                    "drewwalters96":"AT&T",
                    "theyer":"AT&T",
                    "g0r1v3r4":"AT&T",
                    "alop":"Cisco",
                    "fmontei":"AT&T",
                    "sh8121att":"AT&T",
                    "joedborg":"Canonical",
                    "eanylin":"Ericsson",
                    "jezogwza":"AT&T",
                    "stannum-l":"Accenture",
                    "alraddarla":"AT&T",
                    "maris-accenture":"Accenture",
                    "Ciello89":"AT&T",
                    "ss7pro":"AT&T",
                    "dulek":"Intel",
                    "rwellum":"Lenovo",
                    "jaugustine":"AT&T",
                    "mark-burnett":"AT&T",
                    "srwilkers":"AT&T"}

    # Send all contributor information to Keen
    helm_contrib_response = requests.get(HELM_CONTRIBUTORS_URL)
    #kolla_contrib_response = requests.get(KOLLA_CONTRIBUTORS_URL)
    #fuelccp_contrib_response = requests.get(FUELCCP_CONTRIBUTORS_URL)
    armada_contrib_response = requests.get(ARMADA_CONTRIBUTORS_URL)
    deckhand_contrib_response = requests.get(DECKHAND_CONTRIBUTORS_URL)
    drydock_contrib_response = requests.get(DRYDOCK_CONTRIBUTORS_URL)
    shipyard_contrib_response = requests.get(SHIPYARD_CONTRIBUTORS_URL)
    promenade_contrib_response = requests.get(PROMENADE_CONTRIBUTORS_URL)

    headers = {'Accept': 'application/vnd.github.v3.star+json'}
    helm_stargaze_response = requests.get(HELM_STARGAZER_URL, headers=headers)
    #kolla_stargaze_response = requests.get(KOLLA_STARGAZER_URL, headers=headers)
    #fuelccp_stargaze_response = requests.get(FUELCCP_STARGAZER_URL, headers=headers)
    armada_stargaze_response = requests.get(ARMADA_STARGAZER_URL, headers=headers))
    deckhand_stargaze_response = requests.get(DECKHAND_STARGAZER_URL, headers=headers)
    drydock_stargaze_response = requests.get(DRYDOCK_STARGAZER_URL, headers=headers)
    shipyard_stargaze_response = requests.get(SHIPYARD_STARGAZER_URL, headers=headers)
    promenade_stargaze_response = requests.get(PROMENADE_STARGAZER_URL, headers=headers)

    helm_fork_response = requests.get(HELM_FORK_URL).json()
    #kolla_fork_response = requests.get(KOLLA_FORK_URL).json()
    armada_fork_response = requests.get(ARMADA_CONTRIBUTORS_URL)
    deckhand_fork_response = requests.get(DECKHAND_CONTRIBUTORS_URL)
    drydock_fork_response = requests.get(DRYDOCK_CONTRIBUTORS_URL)
    shipyard_fork_response = requests.get(SHIPYARD_CONTRIBUTORS_URL)
    promenade_fork_response = requests.get(PROMENADE_CONTRIBUTORS_URL)

    #helm_commit_response = requests.get(HELM_COMMITS_URL)
    #print json.dumps(helm_commit_response)
    #kolla_commit_response = requests.get(KOLLA_COMMITS_URL).json
    #armada_commit_response = requests.get(ARMADA_COMMITS_URL)
    #deckhand_commit_response = requests.get(DECKHAND_COMMITS_URL)
    drydock_commit_response = requests.get(DRYDOCK_COMMITS_URL)
    shipyard_commit_response = requests.get(SHIPYARD_COMMITS_URL)
    promenade_commit_response = requests.get(PROMENADE_COMMITS_URL)

    commit_affiliations("OpenStack_Helm_Commits", helm_commit_response, contributors)
    #commit_affiliations("Kolla_Kubernetes_Commits", kolla_commit_response, contributors)
    #commit_affiliations("Fuel_CCP_Commits", fuelccp_commit_response, contributors)
    commit_affiliations("Armada_Commits", armada_commit_response, contributors)
    commit_affiliations("Deckhand_Commits", deckhand_commit_response, contributors)
    commit_affiliations("Drydock_Commits", drydock_commit_response, contributors)
    commit_affiliations("Shipyard_Commits", shipyard_commit_response, contributors)
    commit_affiliations("Promenade_Commits", promenade_commit_response, contributors)

    fork_affiliations("OpenStack_Helm_Forks", helm_fork_response, contributors)
    #fork_affiliations("Kolla_Kubernetes_Forks", kolla_fork_response, contributors)
    #fork_affiliations("Fuel_CCP_Forks", fuelccp_fork_response, contributors)
    fork_affiliations("Armada_Forks", armada_fork_response, contributors)
    fork_affiliations("Deckhand_Forks", deckhand_fork_response, contributors)
    fork_affiliations("Drydock_Forks", drydock_fork_response, contributors)
    fork_affiliations("Shipyard_Forks", shipyard_fork_response, contributors)
    fork_affiliations("Promenade_Forks", promenade_fork_response, contributors)
    #for helm_commit in helm_commit_response.json():
    #    keen.add_event("OpenStack_Helm_Commits", helm_commit)

    #for armada_commit in armada_commit_response.json():
    #    keen.add_event("Armada_Commits", helm_commit)

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

    # for helm_response in helm_stargaze_response.json():
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

    starred_data("OpenStack-Helm_Stargazers", helm_stargaze_response)
    starred_data("Armada_Stargazers", armada_stargaze_response)
    starred_data("Drydock_Stargazers", drydock_stargaze_response)
    starred_data("Deckhand_Stargazers", deckhand_stargaze_response)
    starred_data("Shipyard_Stargazers", shipyard_stargaze_response)
    starred_data("Promenade_Stargazers", promenade_stargaze_response)

    additions_over_time_event("OpenStack-Helm_Additions", helm_contrib_response)
    #additions_over_time_event("FuelCCP_Additions", fuelccp_contrib_response)
    #additions_over_time_event("Kolla_Kubernetes_Additions", kolla_contrib_response)
    additions_over_time_event("Armada_Additions", armada_contrib_response)
    additions_over_time_event("Drydock_Additions", drydock_contrib_response)
    additions_over_time_event("Deckhand_Additions", deckhand_contrib_response)
    additions_over_time_event("Promenade_Additions", promenade_contrib_response)
    additions_over_time_event("Shipyard_Additions", shipyard_contrib_response)

    stackalytics_corporate_contributors("OSH_commits", 'openstack-others', 'openstack-helm', 'commits')
    stackalytics_corporate_contributors("OSH_marks", 'openstack-others', 'openstack-helm', 'marks')
    stackalytics_corporate_contributors("OSH_bpd", 'openstack-others', 'openstack-helm', 'bpd')
    stackalytics_corporate_contributors("OSH_patches", 'openstack-others', 'openstack-helm', 'patches')

    stackalytics_corporate_contributors("OSHA_commits", 'openstack-others', 'openstack-helm-addons', 'commits')
    stackalytics_corporate_contributors("OSHA_marks", 'openstack-others', 'openstack-helm-addons', 'marks')
    stackalytics_corporate_contributors("OSHA_bpd", 'openstack-others', 'openstack-helm-addons', 'bpd')
    stackalytics_corporate_contributors("OSHA_patches", 'openstack-others', 'openstack-helm-addons', 'patches')

    stackalytics_engineers("engineers_commits", 'openstack-others', 'openstack-helm', 'commits')
    stackalytics_engineers("engineers_marks", 'openstack-others', 'openstack-helm', 'marks')
    stackalytics_engineers("engineers_bpd", 'openstack-others', 'openstack-helm', 'bpd')
    stackalytics_engineers("engineers_patches", 'openstack-others', 'openstack-helm', 'patches')

    stackalytics_engineers("addons_engineers_commits", 'openstack-others', 'openstack-helm-addons', 'commits')
    stackalytics_engineers("addons_engineers_marks", 'openstack-others', 'openstack-helm-addons', 'marks')
    stackalytics_engineers("addons_engineers_bpd", 'openstack-others', 'openstack-helm-addons', 'bpd')
    stackalytics_engineers("addons_engineers_patches", 'openstack-others', 'openstack-helm-addons', 'patches')



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
