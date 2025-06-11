import whois, random, pandas as pd, datetime, logging, time, concurrent.futures

# Global cache and constants for performance
_current_year = datetime.datetime.now().year
_age_cache = {}

import requests

def get_company_age(domain):
    if not isinstance(domain, str) or domain == "":
        return 0
    domain = domain.strip().replace('http://', '').replace('https://', '').strip('/')
    if domain in _age_cache:
        return _age_cache[domain]
    start_t = time.time()
    # 1. Try Wayback Machine
    wayback_url = f"http://web.archive.org/cdx/search/cdx?url={domain}&output=json&fl=timestamp&limit=1&filter=statuscode:200&from=1996"
    try:
        r = requests.get(wayback_url, timeout=10)
        data = r.json()
        if len(data) > 1:
            first_timestamp = data[1][0]
            year = int(first_timestamp[:4])
            age = max(_current_year - year, 0)
            _age_cache[domain] = age
            logging.debug(f"Wayback: {domain} first seen {year}, age {age} (took {time.time()-start_t:.2f}s)")
            return age
        else:
            logging.debug(f"Wayback: {domain} not found in archive.")
    except Exception as e:
        logging.debug(f"Wayback error for {domain}: {e}")
    # 2. Fallback to WHOIS
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        year = creation_date.year if creation_date else None
        if year:
            age = max(_current_year - year, 0)
            _age_cache[domain] = age
            logging.debug(f"WHOIS: {domain} created {year}, age {age} (took {time.time()-start_t:.2f}s)")
            return age
        else:
            logging.debug(f"WHOIS: {domain} creation year not found.")
    except Exception as exc:
        logging.debug(f"WHOIS failed for {domain}: {exc}")
    # 3. Both failed
    logging.debug(f"Both Wayback and WHOIS failed for {domain}. Returning age 0.")
    _age_cache[domain] = 0
    return 0

def assign_emp_bracket(count):
    if count < 1: return 1
    if count < 50: return 2
    if count < 200: return 3
    return 4
    # 1:1–50, 2:51–200, 3:201–1000, 4:>1000
    # return random.choice([1,2,3,4])

# def seniority_score(title):
#     title = title.lower()
#     if any(x in title for x in ['chief','ceo','cto','founder']): return 10
#     if any(x in title for x in ['vp','head','director']): return 8
#     if any(x in title for x in ['manager','lead']): return 5
#     return 2

def seniority_score(title):
    if not isinstance(title, str):
        return 0 

    title = title.lower()

    if any(x in title for x in ['chief', 'ceo', 'cto', 'founder', 'president', 'exec']):
        return 10

    if any(x in title for x in ['vp', 'head', 'director', 'vice president', 'principal']):
        return 8

    if any(x in title for x in ['manager', 'lead', 'supervisor']):
        return 5

    if any(x in title for x in ['specialist', 'analyst', 'engineer', 'developer', 'associate', 'consultant']):
        return 3
    return 2

def enrich(df, progress_callback=None):
    import math
    overall_start = time.time()
    logging.info("Starting enrichment …")

    # Clean domains
    t0 = time.time()
    df['domain'] = df['website'].str.replace(r'https?://', '', regex=True)
    logging.info("Extracted domains in %.2fs", time.time() - t0)

    # Parallel company-age lookups on unique domains only, with progress
    t0 = time.time()
    unique_domains = df['domain'].dropna().unique()
    logging.info("Fetching company age for %d unique domains", len(unique_domains))
    ages = {}
    total = len(unique_domains)
    if total == 0:
        df['company_age'] = 0
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(20, total)) as ex:
            futures = {ex.submit(get_company_age, domain): domain for domain in unique_domains}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                domain = futures[future]
                try:
                    age = future.result()
                except Exception as exc:
                    age = 0
                ages[domain] = age
                if progress_callback:
                    percent = int((i+1) / total * 100)
                    progress_callback(percent, f"Enriching: {domain} ({i+1}/{total})")
    df['company_age'] = df['domain'].map(ages)
    logging.info("Company ages computed in %.2fs", time.time() - t0)

    # Other lightweight computations (vectorised / fast)
    t0 = time.time()
    df['emp_bracket'] = df['emp_count'].apply(assign_emp_bracket)
    df['seniority'] = df['title'].apply(seniority_score)
    logging.info("Other enrichments computed in %.2fs", time.time() - t0)

    df = df.drop(columns=['website', 'emp_count', 'title'])

    logging.info("Enrichment finished in %.2fs", time.time() - overall_start)
    return df

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="enrich_debug.log",
        filemode="w",
    )

    start_script = time.time()
    logging.info("Reading input CSV …")
    df = pd.read_csv('B2B.csv')
    enriched = enrich(df)
    enriched.to_csv('enriched_sample.csv', index=False)
    logging.info("Script completed in %.2fs", time.time() - start_script)
