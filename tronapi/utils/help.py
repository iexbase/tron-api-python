import re

ip_middle_octet = u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
ip_last_octet = u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"

regex = re.compile(
    u"^"
    # protocol identifier
    u"(?:(?:https?|ftp)://)"
    # user:pass authentication
    u"(?:[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:]+"
    u"(?::[-a-z0-9._~%!$&'()*+,;=:]*)?@)?"
    u"(?:"
    u"(?P<private_ip>"
    # IP address exclusion
    # private & local networks
    u"(?:(?:10|127)" + ip_middle_octet + u"{2}" + ip_last_octet + u")|"
    u"(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + u")|"
    u"(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + u"))"
    u"|"
    # private & local hosts
    u"(?P<private_host>"
    u"(?:localhost))"
    u"|"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    u"(?P<public_ip>"
    u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    u"" + ip_middle_octet + u"{2}"
    u"" + ip_last_octet + u")"
    u"|"
    # IPv6 RegEx from https://stackoverflow.com/a/17871737
    u"\[("
    # 1:2:3:4:5:6:7:8
    u"([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|"
    # 1::                              1:2:3:4:5:6:7::
    u"([0-9a-fA-F]{1,4}:){1,7}:|"
    # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
    u"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"
    # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
    u"([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|"
    # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
    u"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"
    # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
    u"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|"
    # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
    u"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|"
    # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8
    u"[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|"
    # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::
    u":((:[0-9a-fA-F]{1,4}){1,7}|:)|"
    # fe80::7:8%eth0   fe80::7:8%1
    # (link-local IPv6 addresses with zone index)
    u"fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|"
    u"::(ffff(:0{1,4}){0,1}:){0,1}"
    u"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255
    # (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    u"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|"
    u"([0-9a-fA-F]{1,4}:){1,4}:"
    u"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33
    # (IPv4-Embedded IPv6 Address)
    u"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
    u")\]|"
    # host name
    u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
    # domain name
    u"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
    # TLD identifier
    u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
    u")"
    # port number
    u"(?::\d{2,5})?"
    # resource path
    u"(?:/[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:@/]*)?"
    # query string
    u"(?:\?\S*)?"
    # fragment
    u"(?:#\S*)?"
    u"$",
    re.UNICODE | re.IGNORECASE
)

pattern = re.compile(regex)


def string_utf8_to_hex(name):
    return bytes(name, encoding='utf-8').hex()


def is_valid_url(value, public=False):
    """
    Return whether or not given value is a valid URL.

    :param value: URL address string to validate
    :param public: (default=False) Set True to only allow a public IP address
    """
    result = pattern.match(value)
    if not public:
        return bool(result)

    return bool(result)
