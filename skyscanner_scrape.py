import datetime
import Parser
import general
import time
import pandas as pd
import os

def main():
    # Parameters
    start = datetime.datetime.now()
    proxy_path = 'C:\\Users\\dor.lavi\\Google Drive\\flights\\proxy_list.tsv'
    path_to_phantomjs = 'C:/Users/dor.lavi/Google Drive/flights/phantomjs-2.1.1-windows/bin/phantomjs.exe'
    head_csv_path = "./head_data.csv"
    flight_csv_path = "./flight_data.csv"

    url_parser = Parser.URL_parser()
    ny_urls = url_parser.get_ny_urls()
    percent = len(ny_urls) / 100

    for idx, url in enumerate(ny_urls[:20]):
        attempts = 0
        while attempts < 3:
            try:
                # Start connection
                connection = general.Connection(proxy_path=proxy_path, phantomjs_path=path_to_phantomjs)
                driver = connection.get_driver()

                # Get data
                driver.get(url)
                # print "Now we wait 5 seconds..."
                time.sleep(5)

                # Parse the data
                search_test = Parser.flight_parser(driver, url)
                # search_test.print_head()
                # search_test.print_flights()
                head_data, flights_data = search_test.get_data()
                head_data_df = pd.DataFrame([head_data])
                flights_data_df = pd.DataFrame(flights_data)

                # Close connection
                driver.quit()

                # Save the data
                if os.path.exists(head_csv_path): # append if already exists, make a new file if not
                    write_mode = 'a'
                    header_mode = False
                else:
                    write_mode = 'w'
                    header_mode = True
                with open(head_csv_path, write_mode) as f:
                    head_data_df.to_csv(f, mode=write_mode, header=header_mode)

                if os.path.exists(flight_csv_path): # append if already exists, make a new file if not
                    write_mode = 'a'
                    header_mode = False
                else:
                    write_mode = 'w'
                    header_mode = True
                with open(flight_csv_path, write_mode) as f:
                    flights_data_df.to_csv(f, mode=write_mode, header=header_mode)

                # Progress Print
                if idx % percent == 0:
                    print "Already Finished ~ ", idx / percent, "% of the dates at ", datetime.datetime.now().strftime('%d-%b-%Y %H:%M')
                break
            except:
                attempts += 1
                search_test.print_error(attempts)

    print "Time to complete ", datetime.datetime.now()-start

if __name__ == "__main__":
    main()




# source1 = driver.find_element_by_class_name('noUi-handle noUi-handle-lower')
# action = ActionChains(driver)
#
# # move element by x,y coordinates on the screen
# action.drag_and_drop_by_offset(source1, 100, 100).perform()