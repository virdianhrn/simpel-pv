import shortuuid

def generate_short_uuid():
    """
    Membuat ID unik yang pendek dan aman untuk default primary key.
    """
    return shortuuid.uuid()