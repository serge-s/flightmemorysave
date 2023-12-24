# http://www.opensource.org/licenses/mit-license.php MIT License
#
# based on https://github.com/nh13/flightmemory_exporter

import argparse
import re
import sys
import http.cookiejar as cookielib
import mechanize


def main(username, password):
    url_login = 'http://www.flightmemory.com/'

    # open a browser
    br = mechanize.Browser()
    br.set_handle_robots(False)

    # set cookies
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # go through the login page
    br.open(url_login)
    br.select_form(name = "ll")
    br['username'] = username
    br['passwort'] = password
    br.submit()

    # go to the flight data page
    links = list()
    for link in br.links(text_regex="FLIGHTDATA"):
        links.append(link)
    if len(links) == 0:
        print ("Error: likely the login was unsuccessful\n")
        sys.exit(1)
    elif len(links) > 1:
        print ("Error: only one link is expected\n")
        sys.exit(1)
    req = br.click_link(text = "FLIGHTDATA")
    br.open(req)

    dbpos = 50
    page = 1
    while True:
        with open("flightmemory{}.html".format(page), 'wb') as f:
            f.write(br.response().read())
        page += 1

        # follow links to the next page
        # NB: the pattern is important here so that if dbpos=50 we do not choose dbpos=500 too
        links = list()
        pattern = re.compile("%s'" % str(dbpos))
        for link in br.links(url_regex='flugdaten&dbpos=' + str(dbpos)):
            print("Found link:", link)
            if re.search(pattern, str(link)):
                links.append(link)

        if len(links) == 0:
            print("Reached the last page\n")
            break

        if len(links) != 2 and len(links) != 4:
            print("Error: one link is expected, got %d\n" % len(links))
            sys.exit(1)

        for i in range(1, len(links)):
            if links[0].url != links[i].url:
                print("Error: links do not match\n")
                sys.exit(1)

        # go to the next page
        req = br.click_link(url=links[0].url)
        br.open(req)

        # next 50 flights
        dbpos += 50


parser = argparse.ArgumentParser()
parser.add_argument("--username", help = "your flightmemory.com username", required=True)
parser.add_argument("--password", help = "your flightmemory.com password", required=True)
args = parser.parse_args()

main(args.username, args.password)
