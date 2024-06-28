## Readme
While very impressive projects, the vast majority of .onion V3 addresses found on index sites are either inactive or labeled with incorrect meta, due to the privacy, ease of set up and self-hosting, and variation addresses available. 

The goal of this project is to create a local relational database of verified active .onion v3 addresses which can be used for future research projects in image & content classification, as well as analyzing Tor traffic from index ("seeding") through to the end point host. While future development will include parallel processing and multi-threading (both) capabilities, this project is designed to run on a Raspberry Pi 4. 


### Underlying Technologies
- Request through the TOR Nework via SOCKS proxy client (socks5h).
- BeautifulSoup4 for much of the core scraping functionality.
- MariaDB Server and MySQL commands for local database and table creation.

### Database & Tables
The Database and Table structure is designed to emulate the Medallion Architecture which is frequently employed in enterprise environments to create reliable and organized data. Each table name is reflective of the quality and refinement of the data within:
- **Raw Data**: Data here obtained through the process of "seeding". Prior to sending a ping request through the Tor network to each address, redundancies (address & search phrase pairs) are removed.
- **Bronze**: Addresses in this table have been verified as active through a SOCKS request through the Tor network, and given a time stamp of the successful connection. 
- **Silver:** Addresses which have content that can be freely accessed without a password. Building upon the columns from the previous table, the Silver table will include a yes/no value indicating whether or not the site has images presents as well as external links, a value for the service type and the site's top 5 most common words.
- **Gold:** Building on the Silver table, the Gold table will include columns for up to 50 links pointing to external .onion addresses. 

### Workflow & Module Descriptions
![Onion Scraper Workflow](https://github.com/TylerG01/onion_scraper/assets/133159382/023440e5-527e-4c9a-992d-f5e55d21191f)

**onion_sracper(main script):** As the central component of the project, this defines the SOCKS proxy configuration and creates a global requests session within. It then runs the other modules to populate tables in the SQL database and refines it. With this said, each module was built with the ability to run an interdependent script. This is a design consideration for future phases of the project. 

**db_connection:** A duct-tape solution for storing user, password, host and database values used by the other modules. This module will be removed in favor of setting environment variables in the near future. 

1. **db_construction:** Creates the database and table structure outlined above. The database and it's tables utilize Foreign Keys to enforce data integrity.
2. **seeder.py:** When executed, this module utilizes a list of user defined keywords and phrases to build a structured search queries within specified clear net index sites. Samples included: "bitcoin", "gift cards", "crypto", "untraceable", "phone", "email".
3. **duplicates.py:** Once seeder.py completes its queries, this module uses a ‘while True’ loop to repeatedly execute the comparison & deletion logic until no more duplicates are found within the raw table. 
4. **onion_ping:** Accepts a requests.Session object (session) as an argument and uses it to make HTTPS requests through the Tor network to check the status of addresses in the “seed” table. If an address returns a 200 status, it’s moved to the “bronze” table with a timestamp where futher refining will be conducted.
 **content_check.py:** This module iterates through each address in the bronze table and begins to enrich the rows with identifying information. This includes binary values indicating whether or not each address features images and external links.
6. **b2s.py:** Bronze to Silver (b2s) is simply searches the bronze table for the binary value of 1 within either the 'images' or 'Ext_Links' columns. If either columns within the same row contain a true value, then entire row is moved to the silver database. The final version of this project will execute this module periodically.
7. **common_words.py:** This module was created to parse target URL's using Beautiful Soup to extract all text, clean and tokenize the text to focus on descriptive words, then analyze the frequency of the descriptive words to find the top 5 most common to each site. The top 5 words selected appear in descending order, starting from most frequent within the 'common_word_1' column of the silver table.

### Upcoming Features
Once the workflow is fully functional, conditional parallel processing will be added to the onion_scraper.py(main script) to enable the ability to run multiple phases of the work-flow in tandem.  

Additionally, each script in the continuous workflow process (listed as 1 - 7 above) will undergo performance benchmarking to weigh the benefits of multi-threading. 




