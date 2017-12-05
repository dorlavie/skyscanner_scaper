import datetime
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

class flight_parser(object):
    def __init__(self, driver_data, url):
        self.driver_data = driver_data
        self.url = url

    def get_head(self):
        """Return the Best, Cheapest and Fastest routes."""
        delay = 5
        tmp = WebDriverWait(self.driver_data, delay).until(EC.presence_of_element_located((By.ID, 'fqs-tabs')))
        # tmp = self.driver_data.find_element_by_id('fqs-tabs')
        tmp = tmp.text.split('\n')
        head_dict = {}
        head_dict['best_price'] = tmp[1]
        head_dict['best_duration'] = tmp[2]
        head_dict['cheapest_price'] = tmp[4]
        head_dict['cheapest_duration'] = tmp[5]
        head_dict['fastest_price'] = tmp[7]
        head_dict['fastest_duration'] = tmp[8]
        url_parser = URL_parser()
        url_dict = url_parser.parse_url(self.url)
        head_dict['from_city'] = url_dict['from_city']
        head_dict['to_city'] = url_dict['to_city']
        head_dict['from_date'] = url_dict['from_date'].strftime("%d-%b-%Y")
        head_dict['to_date'] = url_dict['to_date'].strftime("%d-%b-%Y")
        return head_dict

    def print_error(self, attempt, error_type):
        try:
            screenshot_path = './screenshots/' + datetime.datetime.now().strftime('%Y%b%d_%H-%M-%S') + '_Error_(' + str(attempt) + ').png'
            self.driver_data.save_screenshot(screenshot_path)
            print "Just got a %s (%s), go look at the screenshots." % (str(error_type), attempt)
            self.driver_data.close()
        except:
            print "Just got a %s (%s), no screenshot neither." % (str(error_type), attempt)

    def print_head(self):
        head = self.get_head()
        print "--------------------------------------------------------------"
        print "search on SkyScanner from %s to %s" % (head['from_city'], head['to_city'])
        print "%s - %s" % (head['from_date'].strftime('%A %d %b %Y'), head['to_date'].strftime('%A %d %b %Y'))
        print "--------------------------------------------------------------"
        print "Best: %s (%s)" % (head['best_price'], head['best_duration'])
        print "Cheapest: %s (%s)" % (head['cheapest_price'], head['cheapest_duration'])
        print "Fastest: %s (%s)" % (head['fastest_price'], head['fastest_duration'])
        print "--------------------------------------------------------------"

    def get_flights(self):
        """Return all the flights in the first page (10 flights)"""
        all_flights = []
        delay = 15
        try:
            WebDriverWait(self.driver_data, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'day-list-item')))
            flights_elemnt = self.driver_data.find_elements_by_class_name("day-list-item")
        except TimeoutException:
            raise ValueError('TimeoutException')
        for flight in flights_elemnt:
            tmp = flight.text.split('\n')
            tmp = [x for x in tmp if not 'perated by' in x]
            tmp = [x for x in tmp if not 'CHANGE AIRPORT' in x]
            flight_detail = {}
            flight_detail['airline'] = tmp[0]
            flight_detail['out_depart_time'] = tmp[1]
            flight_detail['out_from'] = tmp[2]
            flight_detail['out_duration'] = tmp[3]
            flight_detail['out_stops'] = tmp[4]
            flight_detail['out_land_time'] = tmp[5]
            flight_detail['out_to'] = tmp[6]
            flight_detail['in_depart_time'] = tmp[7]
            flight_detail['in_from'] = tmp[8]
            flight_detail['in_duration'] = tmp[9]
            flight_detail['in_stops'] = tmp[10]
            flight_detail['in_land_time'] = tmp[11]
            flight_detail['in_to'] = tmp[12]
            flight_detail['price'] = tmp[14]
            url_parser = URL_parser()
            url_dict = url_parser.parse_url(self.url)
            flight_detail['from_city'] = url_dict['from_city']
            flight_detail['to_city'] = url_dict['to_city']
            flight_detail['to_date'] = url_dict['to_date'].strftime('%A %d %b %Y')
            flight_detail['from_date'] = url_dict['from_date'].strftime('%A %d %b %Y')
            all_flights.append(flight_detail)
        return all_flights

    def print_flights(self):
        page_flights = self.get_flights()
        print "--------------------------------------------------------------"
        print "search on SkyScanner from %s to %s" % (page_flights[0]['from_city'], page_flights[0]['to_city'])
        print "%s - %s" % (page_flights[0]['from_date'], page_flights[0]['to_date'])
        print "--------------------------------------------------------------"
        for flight in page_flights:
            print "%s on %s" % (flight['price'], flight['airline'])
            print "outbound : %s(%s) - %s(%s) %s %s" % (flight['out_depart_time'], flight['out_from'], flight['out_land_time'],
                                                        flight['out_to'], flight['out_stops'], flight['out_duration'])
            print "inbound : %s(%s) - %s(%s) %s %s" % (flight['in_depart_time'], flight['in_from'], flight['in_land_time'],
                                                       flight['in_to'], flight['in_stops'], flight['in_duration'])
            print "--------------------------------------------------------------"

    def get_data(self):
        # head = self.get_head()
        # head['scrape_date'] = datetime.datetime.now().strftime("%d-%b-%Y")
        # head['scrape_time'] = datetime.datetime.now().strftime("%H:%M:%S")
        flights = self.get_flights()
        for dict in flights:
            dict['scrape_date'] = datetime.datetime.now().strftime("%d-%b-%Y")
            dict['scrape_time'] = datetime.datetime.now().strftime("%H:%M:%S")
        # return head, flights
        return flights


class URL_parser(object):
    def __init__(self):
        self.cities_dict = {}
        self.cities_dict['tela'] = 'Tel Aviv'
        self.cities_dict['nyca'] = 'New York'
        self.cities_dict['pari'] = 'Paris'
        self.cities_dict['spka'] = 'Sapporo'
        self.cities_dict['tyoa'] = 'Tokyo'
        self.cities_dict['osaa'] = 'Osaka'


    def get_custom_request(self):
        currency = raw_input("Which Currency? (USD) ")
        from_city = raw_input("What is the origin city name? ")
        to_city = raw_input("What is the destination city name? ")
        from_date = raw_input("When do you want to fly out? (YYMMDD) ")
        to_date = raw_input("When do you want to fly back? (YYMMDD) ")
        from_city = self.get_city_code(from_city)
        to_city = self.get_city_code(to_city)
        self.url = 'https://www.skyscanner.net/transport/flights/%s/%s/%s/%s/?currency=%s' % (from_city, to_city, from_date, to_date, currency)
        # self.url = 'https://www.skyscanner.net/transport/flights/tela/pari/171205/171208/?currency=USD'

    def get_ny_dates(self):
        year = [datetime.datetime.now() + datetime.timedelta(days=x+10) for x in range(355)]
        duration_list = [7, 8, 9, 10, 11, 12, 13, 14]
        dates_list = []
        for day in year:
            for duration in duration_list:
                from_date = day
                duration = datetime.timedelta(days=duration)
                to_date = from_date + duration
                date_dict = {}
                date_dict['from_date'] = from_date.strftime('%y') + from_date.strftime('%m') + from_date.strftime('%d')
                date_dict['to_date'] = to_date.strftime('%y') + to_date.strftime('%m') + to_date.strftime('%d')
                dates_list.append(date_dict)
        return dates_list

    def get_ny_urls(self):
        dates = self.get_ny_dates()
        self.ny_urls = []
        for date in dates:
            tmp_url = 'https://www.skyscanner.net/transport/flights/tela/nyca/%s/%s/?currency=USD' % (date['from_date'], date['to_date'])
            self.ny_urls.append(tmp_url)
        return self.ny_urls

    def get_url(self):
        return self.url

    def get_test_url(self):
        return 'https://www.skyscanner.net/transport/flights/tela/pari/171205/171208/?currency=USD'

    def parse_url(self, url):
        url = url.split('/')
        url_dict = {}
        url_dict['from_city'] = self.get_city_name(url[5])
        url_dict['to_city'] = self.get_city_name(url[6])
        url_dict['from_date'] = datetime.datetime.strptime((url[7]), '%y%m%d')
        url_dict['to_date'] = datetime.datetime.strptime((url[8]), '%y%m%d')
        return url_dict

    def get_city_code(self, city_name):
        for k_city_code, v_city_name in self.cities_dict.iteritems():
            if city_name == v_city_name:
                return k_city_code

    def get_city_name(self, city_code):
        return self.cities_dict[city_code]

    def get_japan_dates(self):
        Sep_dates = [datetime.datetime.strptime('Sep 1 2018', '%b %d %Y') + datetime.timedelta(days=x) for x in range(30)]
        duration_list = range(10, 21)
        dates_list = []
        for day in Sep_dates:
            for duration in duration_list:
                from_date = day
                duration = datetime.timedelta(days=duration)
                to_date = from_date + duration
                date_dict = {}
                date_dict['from_date'] = from_date.strftime('%y') + from_date.strftime('%m') + from_date.strftime('%d')
                date_dict['to_date'] = to_date.strftime('%y') + to_date.strftime('%m') + to_date.strftime('%d')
                dates_list.append(date_dict)
        return dates_list

    def get_japan_urls(self):
        dates = self.get_japan_dates()
        # cities = ['spka', 'tyoa', 'osaa']
        cities = ['tyoa']
        self.japan_urls = []
        for date in dates:
            for city in cities:
                tmp_url = 'https://www.skyscanner.net/transport/flights/tela/%s/%s/%s/?currency=USD' % (city, date['from_date'], date['to_date'])
                self.japan_urls.append(tmp_url)
        return self.japan_urls