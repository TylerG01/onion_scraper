## Readme
While very impressive projects, the vast majority of .onion V3 addresses found on index sites are either inactive or labeled with incorrect meta, due to thee privacy, ease of set up and self-hosting, and variation addresses available. 

The goal of this project is to create a local relational database of verified active .onion v3 addresses which can be used for future research projects in image & content classification, as well as analyzing Tor traffic from index ("seeding") through to the end point host. 



**Database & Tables**
The Database and Table structure is designed to emulate the Medallion Architecture which is frequently employed in enterprise environments to create reliable and organized data. Each table name is reflective of the quality and refinement of the data within:

![Onion_Scraper_Workflow](https://github.com/TylerG01/onion_scraper/assets/133159382/0576fc09-1b24-48ee-90d8-31a0f176bb70)

- **Raw Data**: Data here obtained through the process of "seeding". Prior to sending a ping request through the Tor network to each address, redundancies (address & search phrase pairs) are removed.
- **Bronze**: Addresses in this table have been verified as active through a SOCKS request through the Tor network, and given a time stamp of the successful connection. 
- **Silver:** Addresses which have content that can be freely accessed without a password. Building upon the columns from the previous table, the Silver table will include a yes/no value indicating whether or not the site has images presents as well as external links, a value for the service type and the site's top 5 most common words.
- **Gold:** Building on the Silver table, the Gold table will include columns for up to 50 links pointing to external .onion addresses. 

**Module Inventory & Descriptions:** 
1. **Main:** As the central component of the project, this defines the SOCKS proxy configuration and creates a global requests session within. It then runs the other modules to populate tables in the SQL database and refines it. 
2. **db_connection:** A duct-tape solution for storing user, password, host and database values used by the other modules. This module will be removed in favor of setting environment variables in the near future. 
3. **db_construction:** Creates the database and table structured outlined above.
4. **seeder.py:** When executed, this module utilizes a list of user defined keywords and phrases to build a structured search querie within specified clear net index sites. Samples included: 
5. **duplicates.py:** Once raw.py completes its queries, this module uses a ‘while True’ loop to repeatedly execute the comparison & deletion logic until no more duplicates are found within the raw table. 
6. **onion_ping:** Accepts a requests.Session object (session) as an argument and uses it to make HTTPS requests through the Tor network to check the status of addresses in the “seed” table. If an address it live, it’s moved to the “bronze” table with a timestamp where futher refining will be conducted. 
