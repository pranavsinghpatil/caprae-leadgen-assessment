from faker import Faker
import csv
import random

def generate_fake_leads(num_records=50000):
    fake = Faker()
    
    # List of realistic company suffixes
    company_suffixes = ['Inc.', 'LLC', 'Corp.', 'Technologies', 'Solutions', 'Group', 'Industries']
    
    # List of job positions
    positions = [
        'CEO', 'CTO', 'CFO', 'COO',
        'Director of Engineering', 'Technical Director', 'Project Manager',
        'Senior Manager', 'Product Manager', 'Operations Manager',
        'Team Lead', 'Department Head',
        'Senior Engineer', 'Software Engineer', 'Systems Analyst',
        'Sales Manager', 'Marketing Manager', 'HR Manager',
        'Business Analyst', 'Account Manager',
        'Employee', 'Associate', 'Specialist'
    ]
    
    # List of email domains
    email_domains = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'aol.com', 'icloud.com', 'protonmail.com', 'zoho.com',
        'mail.com', 'fastmail.com', 'yandex.com', 'gmx.com'
    ]
    
    # Generate fake data
    leads = []
    used_emails = set()  # To ensure unique emails
    
    while len(leads) < num_records:
        name = fake.name()
        # Create email with first initial and last name
        email_name = f"{name.split()[0][0].lower()}{name.split()[-1].lower()}"
        email_domain = random.choice(email_domains)
        email = f"{email_name}{random.randint(1, 999)}@{email_domain}"
        
        # Ensure email is unique
        if email not in used_emails:
            used_emails.add(email)
            company = f"{fake.company().replace(', Inc.', '')} {random.choice(company_suffixes)}"
            post = random.choice(positions)
            leads.append([name, email, company, post])
    
    # Write to CSV
    output_file = 'demo_data/raw_leads.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'email', 'company', 'post'])  # Header
        writer.writerows(leads)
    
    print(f"Generated {num_records} fake leads in {output_file}")

if __name__ == '__main__':
    generate_fake_leads(50000)  # Generate 50000 leads