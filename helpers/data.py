import uuid

PASSWORD = "Passw0rd"


def new_username():
    """Return a unique username so that every test registers its own customer."""
    return f"qa_{uuid.uuid4().hex[:12]}"


def registration_form(username, password=PASSWORD, repeated_password=None):
    """Return the registration form fields, keyed by the ParaBank field name.

    The confirmation field repeats the password unless `repeated_password` is given.
    """
    return {
        "customer.firstName": "Test",
        "customer.lastName": "User",
        "customer.address.street": "1 Test Street",
        "customer.address.city": "Testville",
        "customer.address.state": "TS",
        "customer.address.zipCode": "12345",
        "customer.phoneNumber": "5550100",
        "customer.ssn": "123-45-6789",
        "customer.username": username,
        "customer.password": password,
        "repeatedPassword": password if repeated_password is None else repeated_password,
    }
