import whois, random, pandas as pd, datetime

def get_company_age(domain):
    try:
        w = whois.whois(domain)
        year = w.creation_date.year
    except:
        year = datetime.datetime.now().year
    return datetime.datetime.now().year - year

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

def enrich(df):
    df['domain'] = df['website'].str.replace(r'https?://','')
    df['company_age'] = df['domain'].apply(get_company_age)
    df['emp_bracket'] = df['emp_count'].apply(assign_emp_bracket)
    df['seniority'] = df['contact_title'].apply(seniority_score)
    return df

df = pd.read_csv('B2B.csv')
enriched = enrich(df)
enriched.to_csv('data/enriched_sample.csv',index=False)
