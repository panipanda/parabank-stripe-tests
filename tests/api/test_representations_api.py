import xml.etree.ElementTree as ET
from decimal import Decimal

import requests

from config import BASE_URL, TIMEOUT
from helpers.api import get_json


def test_account_json_and_xml_are_equivalent(new_user):
    # TC-23: the same account requested as JSON and as XML comes back with the matching
    # content type and the same id, customerId, type and numeric balance
    customer_id = new_user["customer_id"]
    account_id = get_json(f"/customers/{customer_id}/accounts")[0]["id"]
    url = f"{BASE_URL}/accounts/{account_id}"

    as_json = requests.get(url, headers={"Accept": "application/json"}, timeout=TIMEOUT)
    as_xml = requests.get(url, headers={"Accept": "application/xml"}, timeout=TIMEOUT)

    assert as_json.status_code == 200, f"JSON: expected status 200, got {as_json.status_code}"
    assert as_xml.status_code == 200, f"XML: expected status 200, got {as_xml.status_code}"
    assert as_json.headers["Content-Type"].startswith("application/json"), (
        f"Expected a JSON content type, got {as_json.headers['Content-Type']!r}"
    )
    assert as_xml.headers["Content-Type"].startswith("application/xml"), (
        f"Expected an XML content type, got {as_xml.headers['Content-Type']!r}"
    )

    json_account = as_json.json(parse_float=Decimal)
    xml_account = ET.fromstring(as_xml.text)
    assert xml_account.tag == "account", f"Expected root element 'account', got {xml_account.tag!r}"

    assert int(xml_account.findtext("id")) == json_account["id"], (
        f"id differs: JSON {json_account['id']}, XML {xml_account.findtext('id')}"
    )
    assert int(xml_account.findtext("customerId")) == json_account["customerId"], (
        f"customerId differs: JSON {json_account['customerId']}, "
        f"XML {xml_account.findtext('customerId')}"
    )
    assert xml_account.findtext("type") == json_account["type"], (
        f"type differs: JSON {json_account['type']!r}, XML {xml_account.findtext('type')!r}"
    )
    assert Decimal(xml_account.findtext("balance")) == json_account["balance"], (
        f"balance differs: JSON {json_account['balance']}, XML {xml_account.findtext('balance')}"
    )
