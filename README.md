
yeah, I will add async endpoints, I swear
<h1>1. Description</h1>
This project is about scraping GPU from <a href="https://www.newegg.com/" target="_blank">new egg</a>, adding data to database, do operations on the data using api, running scraper with it as well and in the end deisplaying the data in dash web app.

[![video](https://img.youtube.com/vi/Cw-WgAwtPD4/0.jpg)](https://www.youtube.com/watch?v=Cw-WgAwtPD4)

<h1>2. Requirements</h1>
<ol>
  <li>Python 3.9</li>
  <li>Packages from requirements.txt file</li>
</ol>

<h1>3. Components</h1>
<ol>
  <li>Scraper</li>
  <li>Database</li>
  <li>Api</li>
  <li>Web app</li>
</ol>


<h1>3.1 Scraper</h1>
<p>This is headless scraper made completely using requests that are sent asynchronously and using proxy in ip:port:user:pass format. Requests are made asynchronously to make whole process faster and proxy is used, so it won't get blocked (wow). We focus on GPUs only that's why it looks for a products in category id = 100007709, for example: https://www.newegg.com/p/pl?SrchInDesc=radeon+rx+580&N=100007709&PageSize=60.
<br>
<br>
Both products details and reviews are being scraped, results are saved in 2 different json files (but in the same folder) in the sink folder. Folder with data is called data_{execution_id}_{intDateyyyymmdd}_{HHMMSSfff}, json files within data folder have the same time id and execution id but you replace data with Products/Reviews.</p>
<br>
<ul>Parameters:
  <li><strong>phrase : int</strong> - phrase you look for, if there are is no such thing, scraper will save empty files (maybe not the best, but who cares)</li>
  <li><strong>max_pages : int, default: 0</strong> - when set to 0, it will take all pages</li>
  <li><strong>execution_id : str, default: "0"</strong> - when using api it's generated automatically, when using scraper you can provide whatever int you want</li>
  <li><strong>save : bool, default: True</strong> - saving to sink folder. <strong>BTW in api you don't have a choice XD it's always true cuz I forgot and didn't care lmao</strong></li>
</ul>


<h1>3.2 Database</h1>
<p>As database I used sqlalchemy(sqlite), it contains the following tables: <strong>Products, Reviews, SpeschulUsers</strong>. See <strong>database/models.py</strong></p>
<ol>
  <li><strong>Products</strong> - stores products, it has relationship with <strong>Reviews</strong> table. This table contains historical data of products, <strong>Archive</strong> column is really important here - when record has <strong>Archived</strong> set to false, then this is the most recent records, if not it's historical record.</li>
  <li><strong>Products</strong> - stores reviews, it has relationship with <strong>Products</strong> table. <strong>ProductId</strong> is a foreign key.</li>
  <li><strong>SpeschulUsers</strong> - stores users with special roles, for now it has only Admin user with admin role (admin is the only role), becuase most of endpoints in API are protected by password, so you use this user to authenticate. </li>
</ol>

<h4>Db services - database/db_services.py</h4>
<p>To simplify things, I've created function to perform different operations on database (and sink folder), like delete, insert, update, select. These operations (except of insert) have 2 functions each - one uses ORM and the other gives user more freedom when it comes to setting WHERE clause and SELECT, COUNTs, SUMs GROUP BY and other stuff</p>

![Screenshot_3](https://github.com/Koks-creator/NewEggGPUs/assets/73878161/079d515b-e3a7-4aa9-8159-79d604d6122c)

![Screenshot_4](https://github.com/Koks-creator/NewEggGPUs/assets/73878161/d749e0eb-361d-404c-8690-0acc465b2a12)

When it comes to insert, I wanted it to be inserted only from scraped data (so no manual insert unless you do it directly on database by creating your own query). Data is added using <strong>add_data_from_sink</strong>. Products are being checked for duplicates to avoid duplicated record and checks if some column is different, if in db we have product with id 'MYID' and product with same id has been scraped but price has changed then old record is being archived (Archived set to true) and new active (Archived set to false) record is being created. Reviews are being checked only for duplicates.


<h3><strong>Database is being created in setup.py file and it also includes creating admin user</strong></h3>

<h1>3.3 API</h1>
It's used for db operations, running scraper, managing sink folder. It works on port 8000. I'm too lazy to describe all of these endpoints and schemas, just see /docs endpoint and <a href="https://www.youtube.com/watch?v=CUoitT-Qhmg" target="_blank">read</a> goddam code.

![Screenshot_5](https://github.com/Koks-creator/NewEggGPUs/assets/73878161/4f5a8524-9892-4ab4-8af3-e9813214a98f)

![Screenshot_6](https://github.com/Koks-creator/NewEggGPUs/assets/73878161/b67a85a1-7470-469a-af09-8bc5d1d3e236)

<h1>3.4 Web app</h1>
<p>Web app made in dash (superapp/gpu_app.py), you've probably saw how it works and looks like cuz there is video at the top of this readme. It's used for visualizing data, that's it. Oh, and it works on port 8050 (I guess it's a default dash port).</p>


