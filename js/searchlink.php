<?Php
//Requested by JavaScript in addissue_web_form.php to get search link for a torrent site
require '../class.php';
$scanindex=new scanindex;
$st_site=$scanindex->db_scanindex->prepare("SELECT * FROM torrentsites WHERE name=?");
$st_site->execute(array($_GET['site']));
$siteinfo=$st_site->fetch(PDO::FETCH_ASSOC);
//print_r($siteinfo);
$search=$_GET['search'];	
echo $siteinfo['searchurl'].$search;