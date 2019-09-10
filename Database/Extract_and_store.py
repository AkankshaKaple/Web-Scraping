from bs4 import BeautifulSoup
from googlesearch import search
import json
from pymongo import MongoClient
from flask import Flask, request, jsonify
from bson import ObjectId

app = Flask(__name__)
client = MongoClient()
db = client.F_Database
# Company_Name = 'Niyo Solutions'
HTMLs = ['funding.html', 'jobs.html', 'linkedin.html', 'main.html',
         'people.html', 'crunch_base.html']

html_data = {}
for html in HTMLs:
    with open('HTML-file/niyo/' + html, 'r') as file:
        data = file.read()
    html_data[html.replace('.html', '')] = data

print(html_data.keys())


# Angel.co
def jobs(html_page, reference_id):
    soup = BeautifulSoup(html_page, features="html.parser")
    current_jobs = soup.findAll(class_='component_e6bd3 expanded_80d76')
    software_jos = [job.text for job in current_jobs if 'Software' in job.text]
    job_info = {}
    for index in range(len(software_jos)):
        Jobs = {}
        job = software_jos[index]
        job = job.replace('Software Engineering', '').replace('₹', '***').replace('•', '***').replace('%Apply now', '')
        job = job.split('***')
        ch = list(job[0])
        for i in range(1, len(ch)):
            if (('a' <= ch[i] <= 'z') or (ch[i] == ')')) and ('A' <= ch[i + 1] <= 'Z'):
                Jobs['Title'] = job[0][:i + 1]
                Jobs['Location'] = job[0][i + 1:]
                break
        Jobs['Salary'] = job[1] + job[2]
        job_info['Job_' + str(index)] = Jobs
    job_info['Reference_id'] = reference_id
    db.Jobs.insert(job_info)
    return job_info


# Angel.co
def details(html_page):
    soup = BeautifulSoup(html_page, features="html.parser")
    detail_info = {'Detail': soup.find_all(class_='description_f92d0')[0].text}

    area_of_interest = []
    for i in soup.find_all(class_='styles_component__3BR-y'):
        area_of_interest.append(i.text)

    detail_info['Area_of_interest'] = area_of_interest
    return detail_info


# Crunch base
def funding(html_page, reference_id):
    soup = BeautifulSoup(html_page, features="html.parser")
    fund = {'Total_funding': soup.find(class_='component_43375').text.split(' ')[0].replace('Funding', '')[:-1],
            'funding_rounds': soup.find(class_='component_43375').text.split(' ')[0].replace('Funding', '')[
                              -1:]}

    round_info = soup.findAll(class_='amountRaised_3c2b1')
    round_info.reverse()
    round_list = ['Seed', 'A', 'B', 'C', 'D']
    j = 0
    for i in round_info:
        if round_list[j] == 'Seed':
            fund[round_list[j]] = i.text
            j += 1
        else:
            fund['Round ' + round_list[j]] = i.text
            j += 1

    fund['Reference_id'] = reference_id
    db.Funding.insert(fund)
    return fund


# Crunch base
def Founder(html_page, reference_id):
    soup = BeautifulSoup(html_page, features="html.parser")
    parameters = ['Total Funding Amount', 'Number of Funding Rounds', 'Number of Lead Investors',
                  'Monthly Visits', 'Owler Estimated Revenue', 'Number of Current Team Members']
    keywords = ['Chief', 'Executive', 'Officer', 'Associate', 'President',
                'Technology Evangelist', 'Co-Founder', 'CoFounder', 'Founder']

    info = [i.text for i in soup.findAll(class_='even')]
    Company_Information = {}
    founder = {}
    index = 0
    for i in info:
        data = i.strip().split('\xa0')
        value = data[-1]
        key = i.replace(value, '').replace('\xa0', '')
        if key in parameters:
            Company_Information[key] = value

        for keyword in keywords:
            f = {}
            if keyword.lower() in i.lower():
                value = i.strip().split(' ')
                name = value[0] + " " + value[1]
                f['Name'] = name
                f['Position'] = i.replace(name, '')
                founder['Founder_' + str(index)] = f
                index += 1
                break
    crunch_base_data = {'Founder': founder, 'Company_Information': Company_Information}
    crunch_base_data['Founder']['Reference_id'] = reference_id
    crunch_base_data['Company_Information']['Reference_id'] = reference_id
    db.Founder.insert(crunch_base_data['Founder'])
    db.Company_Information.insert(crunch_base_data['Company_Information'])
    return crunch_base_data


# Snov io
def contact_person(domain_name):
    contact_info = {'domain': 'https://www.goniyo.com/',
                    'webmail': False,
                    'result': 1,
                    'limit': 1,
                    'offset': 0,
                    'companyName': 'Niyo Solutions Inc.',
                    'emails': [{'email': 'vinay@goniyo.com',
                                'type': 'prospect',
                                'status': 'verified',
                                'firstName': 'Vinay',
                                'lastName': 'Bagri',
                                'position': 'CEO and Co-founder',
                                'sourcePage': 'https://www.linkedin.com/in/vinayniyo/'}],
                    'email': 'vinay@goniyo.com',
                    'type': 'prospect',
                    'status': 'verified',
                    'firstName': 'Vinay',
                    'lastName': 'Bagri',
                    'position': 'CEO and Co-founder',
                    'sourcePage': 'https://www.linkedin.com/in/vinayniyo/'}
    return contact_info


def print_data(data_id):
    print('Print data')
    Company_Name_by_document = ''
    cursor_1 = db.Company_Data.find({'_id': ObjectId(data_id)})
    for data_1 in cursor_1:
        Company_Name_by_document = data_1['Company_Name']

    print(Company_Name_by_document)

    ref_id = ''
    data_dict = {}
    # Company_Data
    cursor = db.Company_Data.find({'Company_Name': Company_Name_by_document})
    for data in cursor:
        ref_id = data['_id']
        # print(type(ref_id), type(data['_id']))
        # print(ref_id, data['_id'])
        data['_id'] = str(data['_id'])
        data_dict['Company_Data'] = data
        break

    # Company_Information
    cursor = db.Company_Information.find({'Reference_id': str(ref_id)})
    for data in cursor:
        print(type(ref_id), type(data['_id']))
        data['_id'] = str(data['_id'])
        data_dict['Company_Information'] = data
        break

    # Contact_Person
    cursor = db.Contact_Person.find({'Reference_id': str(ref_id)})
    for data in cursor:
        data['_id'] = str(data['_id'])
        data_dict['Contact_Person'] = data
        break

    # Founder
    cursor = db.Founder.find({'Reference_id': str(ref_id)})
    for data in cursor:
        data['_id'] = str(data['_id'])
        data_dict['Founder'] = data
        break

    # Funding
    cursor = db.Funding.find({'Reference_id': str(ref_id)})
    for data in cursor:
        data['_id'] = str(data['_id'])
        data_dict['Funding'] = data
        break

    # Jobs
    cursor = db.Company_Information.find({'Reference_id': str(ref_id)})
    for data in cursor:
        data['_id'] = str(data['_id'])
        data_dict['Company_Information'] = data
        break

    # URLs
    cursor = db.URLs.find({'Reference_id': str(ref_id)})
    for data in cursor:
        data['_id'] = str(data['_id'])
        data_dict['URLs'] = data
        break
    return data_dict


# Google library
def get_urls(company_name):
    sites = ['LinkedIn', 'Angel_co', 'Tech_crunch', 'Website']
    urls = {}
    for site in sites:
        query = company_name + site
        url_generator = search(query, tld="com", num=1, stop=1, pause=2)
        for url in url_generator:
            urls[site] = url
    db.URLs.insert(urls)
    return urls


def available_data(data_dict, urls):
    angel = ["Round A", "Round B", "Round c", "Round D", "Seed", "Total_funding", "funding_rounds"]
    crunch_base = ["Area_of_interest", "Founder", "Company_Information"]
    linked_in = ['Employee', 'Location']
    angel_data = {}
    crunch_base_data = {}
    dict_2 = {}
    linked_in_data = {}
    key_list = []
    for key in data_dict.keys():
        key_list = key_list + list(data_dict[key])
        dict_2 = {**dict_2, **data_dict[key]}

    for val in key_list:
        if val in angel:
            angel_data[val] = dict_2[val]
        if val in crunch_base:
            crunch_base_data[val] = dict_2[val]
        if val in linked_in:
            linked_in_data[val] = dict_2[val]

        crunch_base_data['url'] = urls['Tech_crunch']
        linked_in_data['url'] = urls['LinkedIn']
        angel_data['url'] = urls['Angel_co']

    return json.dumps({'crunch_base_data': crunch_base_data, 'angel_co_data': angel_data, 'linked_in_data': linked_in_data})


@app.route('/send_urls', methods=['GET', 'POST'])
def send_urls(urls):
    print('Check if company data already exists in database')
    cursor = db.Company_Data.find()
    for cursor_data in cursor:
        # check if company website already exists in database
        if urls['Website'] == cursor_data['Website']:
            data_id = str(cursor_data['_id'])
            print('Company already exists in database')
            # Check if everything is present in the database
            return available_data(print_data(data_id), urls)
        else:
            print('Company does not exist in database')
            return available_data({}, urls)


@app.route('/company_detail', methods=['POST'])
def company_detail():
    # Get URLs of related to company
    company_name = request.form['company_name']
    urls = get_urls(company_name)

    return send_urls(urls)


@app.route('/get_html_page', methods=['GET','POST'])
def get_html_page():
    # json_data = request.get_json()
    # key = json_data['key']
    # html_content = json_data['value']
    # website = json_data['Website']
    global urls
    website = "https://www.goniyo.com/"
    cursor = db.URLs.find({'Website': website})
    for i in cursor:
        urls = i
        break

    # Contact_person
    contact_info = contact_person(urls['Website'])

    # Company_detail
    company_info_ac = details(html_data['main'])

    # Company_Data
    db.Company_Data.insert({'Website': urls['Website'],
                            "Company_Name": contact_info['companyName'],
                            'Area_of_interest': company_info_ac['Area_of_interest']
                            })

    # Get primary key for the document
    cursor = db.Company_Data.find({'Company_Name': contact_info['companyName']})
    reference_id = ''
    for cursor_data in cursor:
        reference_id = str(cursor_data['_id'])
        break

    # Contact_Person_document
    db.Contact_Person.insert({'First_Name': contact_info['firstName'],
                              'Last_Name': contact_info['lastName'],
                              'Position': contact_info['position'],
                              'LinkedIn_Profile': contact_info['sourcePage'],
                              'Email': contact_info['email'],
                              'Reference_id': reference_id
                              })

    # Jobs_document
    jobs(html_data['jobs'], reference_id)

    # Founders_document and Comp_info_document
    founder = Founder(html_data['crunch_base'], reference_id)

    # funding_document
    funding(html_data['funding'], reference_id)
    return print_data(reference_id)


if __name__ == '__main__':
    app.run(debug=True)
