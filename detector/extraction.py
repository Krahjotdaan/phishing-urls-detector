import re
import math
import urllib
import numpy as np
from detector.config import *

def entropy(s):
    if not s:
        return 0.0
    prob = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)

def rule_based_phish(url):
    return '@' in url

def extract_features(url):
    has_scheme_orig = url.startswith(('http://', 'https://'))
    parse_url = url if has_scheme_orig else 'http://' + url
    
    try:
        parsed = urllib.parse.urlparse(parse_url)
        netloc = parsed.netloc
        
        if netloc.startswith('xn--'):
            netloc = netloc.encode('ascii').decode('idna')
        
        normalized_url = parsed._replace(netloc=netloc).geturl()
        url = normalized_url
    except:
        pass
    
    has_scheme = url.startswith(('http://', 'https://'))
    parse_url = url if has_scheme else 'http://' + url
    
    try:
        parsed = urllib.parse.urlparse(parse_url)
        netloc = parsed.netloc.lower()
        path = parsed.path.lower()
    except:
        netloc = path = ""
    
    num_slashes = url.count('/')
    num_exclam = url.count('!')
    num_at = url.count('@')
    num_dollar = url.count('$')
    num_dots = netloc.count('.')
    len_netloc = len(netloc)
    dot_density = num_dots / (len_netloc + 1e-6)
    len_url = len(url)
    path_depth = max(0, num_slashes - 2)
    
    parts = netloc.split('.') if netloc else []
    subdomain = '.'.join(parts[:-2]) if len(parts) > 2 else ""
    is_random_subdomain = (
        len(subdomain) > 10 and 
        subdomain.isalnum() and 
        not any(brand in subdomain for brand in ['www', 'mail', 'blog'])
    )
    
    random_strings = re.findall(r'[a-zA-Z0-9]{10,}', path)
    has_random_string_in_path = len(random_strings) > 0
    
    clean_netloc = netloc.replace('.', '').replace('-', '')
    domain_entropy = entropy(clean_netloc) if clean_netloc else 0.0
    
    part_lengths = [len(part) for part in parts] if parts else [0]
    domain_length_std = np.std(part_lengths) if len(part_lengths) > 1 else 0.0
    
    digit_count = sum(c.isdigit() for c in netloc)
    digit_ratio = digit_count / (len(netloc) + 1e-6)
    
    return np.array([
        num_slashes,
        num_exclam,
        num_at,
        num_dollar,
        dot_density,
        len_netloc,
        len_url,
        path_depth,
        int(is_random_subdomain),
        int(has_random_string_in_path),
        domain_entropy,
        domain_length_std,
        digit_ratio
    ], dtype=np.float32)

def url_to_seq(url, max_len=MAX_LEN):
    if not isinstance(url, str):
        url = ""
    url = url.lower()
    seq = [char_to_id.get(c, 0) for c in url[:max_len]]
    return seq + [0] * (max_len - len(seq))
