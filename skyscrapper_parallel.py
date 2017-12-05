import multiprocessing as mp
import datetime
import Parser
import general
import time
import pandas as pd
import os

path_prefix = datetime.datetime.now().strftime('%y%m%d')
proxy_path = './proxy_list.tsv'
user_agent_path = './user_agent_list.csv'
path_to_phantomjs = 'C:/Users/dor.lavi/Google Drive/flights/phantomjs-2.1.1-windows/bin/phantomjs.exe'
head_csv_path = "./flights/%s_head_data.csv" % path_prefix
flight_csv_path = "./flights/%s_flight_data.csv" % path_prefix

def worker(url, q):
    attempts = 0
    while attempts < 3:
        try:
            # Start connection
            connection = general.Connection(proxy_path=proxy_path, user_agent_path=user_agent_path, phantomjs_path=path_to_phantomjs)
            driver = connection.get_driver()

            # Get data
            driver.get(url)

            # Parse the data
            search_test = Parser.flight_parser(driver, url)
            # head_data, flights_data = search_test.get_data()
            flights_data = search_test.get_data()
            # head_data_df = pd.DataFrame([head_data]).to_csv(header=False)
            flights_data_df = pd.DataFrame(flights_data).to_csv(header=False)

            # Close connection
            driver.quit()
            res = dict(
                # head=head_data_df,
                flight=flights_data_df
            )
            q.put(res)
            # print "Finished URL %s" % url
            return res
        except ValueError as err:
            attempts += 1
            search_test.print_error(attempts, err.args[0])
            driver.quit()

def listener(q):
    '''listens for messages on the q, writes to file. '''
    # head_f = open(head_csv_path, 'wb')
    flight_f = open(flight_csv_path, 'wb')
    flight_f.write(',airline,from_city,from_date,in_depart_time,in_duration,in_from,in_land_time,in_stops,in_to,out_depart_time,out_duration,'
                   'out_from,out_land_time,out_stops,out_to,price,scrape_date,scrape_time,to_city,to_date\n')
    flight_f.flush()
    while 1:
        m = q.get()
        if m == 'Done':
            # head_f.write('End Of File - Success')
            flight_f.write('End Of File - Success')
            break
        # head_f.write(m['head'])
        flight_f.write(m['flight'])
        # head_f.flush()
        flight_f.flush()
    # head_f.close()
    flight_f.close()

def main():
    start = datetime.datetime.now()
    print "Starting at %s" % start
    url_parser = Parser.URL_parser()
    japan_urls = url_parser.get_japan_urls()
    url = japan_urls[0]

    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(5)

    # put listener to work first
    watcher = pool.apply_async(listener, (q,))

    # fire off workers
    jobs = []
    for url in japan_urls:
        job = pool.apply_async(worker, (url, q))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    for idx, job in enumerate(jobs):
        job.get()
        if idx%(len(jobs)/100) == 0 :
            print "Finished %.2f%% at %s" % (float(idx) / len(jobs) * 100.0, datetime.datetime.now())

    # now we are done, kill the listener
    q.put('Done')
    pool.close()
    pool.join()

    print "Time to complete ", datetime.datetime.now()-start


if __name__ == "__main__":
    main()
