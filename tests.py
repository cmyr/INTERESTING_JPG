# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests

sample_response = """<img id="result-img" src="../tmpfiles/20141227-18:46:44.jpg" height="300"/><h4>TAGS:</h4><h4>&nbsp;&nbsp;bridges&nbsp;&nbsp;wharf&nbsp;&nbsp;buidings&nbsp;&nbsp;bridge&nbsp;&nbsp;buildings&nbsp;&nbsp;</h4><br/><h4>Nearest Neighbor Sentence:</h4><ul><li>people walking on a bridge that has a small roof over it .</li></ul><br/><h4>Top-5 Generated:</h4><ul><li>a group of people walking down the buildings on a large bridge .</li><li>people are walking down a bridge .</li><li>two people walking down a bridge .</li><li>some buildings and people walking down a bridge .</li><li>four people are walking down a bridge .
</li></ul>"""

def raw_text_from_image(image_url):
    base_url = 'http://deeplearning.cs.toronto.edu/api/url.php'
    files = {
    'urllink': ('', image_url),
    'url-2txt': ('', '')
    }
    headers = {'connection': 'keep-alive', 'X-Requested-With': 'XMLHttpRequest'}
    return requests.post(base_url, files=files, headers=headers)


    # http://graphics8.nytimes.com/images/2014/12/28/opinion/sunday/2014-yip-august-slide-0F09/2014-yip-august-slide-0F09-jumbo.jpg
# ------WebKitFormBoundary5cTwys3Ujbn5yjUm
# Content-Disposition: form-data; name="urllink"

# http://graphics8.nytimes.com/images/2014/12/28/opinion/sunday/2014-yip-february-slide-6MH0/2014-yip-february-slide-6MH0-jumbo.jpg
# ------WebKitFormBoundary5cTwys3Ujbn5yjUm
# Content-Disposition: form-data; name="url-2txt"

# deeplearning.cs.toronto.edu resource-type-xhr   POST    HTTP    200     645 614 1.3471217155456543  10.155226945877075  0.0244600772857666
# ------WebKitFormBoundary5cTwys3Ujbn5yjUm--





def main():
    test_url = 'http://graphics8.nytimes.com/images/2014/12/28/opinion/sunday/2014-yip-august-slide-0F09/2014-yip-august-slide-0F09-jumbo.jpg'
    r = raw_text_from_image(test_url)
    print(r.text)

if __name__ == "__main__":
    main()