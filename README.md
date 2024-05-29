

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
Both products details and reviews are being scraped, results are saved in 2 different json files (but in the same folder) in the sink folder. Folder with data is called data_{execution_id}_{intDateyyyymmdd}_{HHMMSSfff}, json files within data folder have the same time id and execution id but you replace data with Products/Reviews</p>
<br>
<ul>Parameters:
  <li><strong>phrase : int</strong> - phrase you look for, if there are is no such thing, scraper will save empty files (maybe not the best, but who cares)</li>
  <li><strong>max_pages : int, default: 0</strong> - when set to 0, it will take all pages</li>
  <li><strong>execution_id : str, default: "0"</strong> - when using api it's generated automatically, when using scraper you can provide whatever int you want</li>
  <li><strong>save : bool, default: True</strong> - saving to sink folder. <strong>BTW in api you don't have a choice XD it's always true cuz I forgot and didn't care lmao</strong></li>
</ul>

