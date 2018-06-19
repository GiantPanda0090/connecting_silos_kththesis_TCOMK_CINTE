import requests
import json


with open('config.json') as json_data_file:
    configuration = json.load(json_data_file)
    canvas = configuration['canvas']
    access_token = canvas["access_token"]
    # access_token=configuration["canvas"]["access_token"]
    # baseUrl = 'https://kth.instructure.com/api/v1/courses/' # changed to KTH domain
    baseUrl = 'https://%s/api/v1/courses/' % canvas.get('host', 'kth.instructure.com')
    header = {'Authorization': 'Bearer ' + access_token}

def main():
    r=requests.post('https://kth.instructure.com/courses/2139/assignments/24565/submissions?zip=1?access_token='+access_token,allow_redirects=True)
    print r.content
    with open("code3.zip", "wb") as code:
        code.write(r.content)


if __name__ == "__main__": main()
