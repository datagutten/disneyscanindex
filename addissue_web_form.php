<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Add issue</title>
</head>

<body>
<?php
ini_set('display_errors',true);
require 'class.php';
$scanindex=new scanindex;
require 'datalist.php';
if(isset($_GET['file']))
	$file=$_GET['file'];
else
	$file='';

?>
<script type="text/javascript" src="js/addissue_web_form.js"></script>

<?Php
	$st_sites=$scanindex->db_scanindex->query("SELECT * FROM torrentsites");
	$sites=$st_sites->fetchAll(PDO::FETCH_ASSOC);
	echo datalist('torrentsites',array_column($sites,'name'));
	$publication='';
if(!empty($file))
{
	echo '<span id="searchstring" style="display:none">'.preg_replace('/(.+?)\(.+/','$1',basename($file))."</span>\n";
	echo "<p>Adding <span id=\"file\">{$file}</span></p>\n";
//Try to find issue or publication from file path and name
if(preg_match("^{$scanindex->filepath}/([a-z]+)\-(.+?)/([0-9\-]*).+^",$file,$issueinfo))
{
	if($scanindex->validate_issue_code($issueinfo[1].'/'.$issueinfo[2].$issueinfo[3],'issue'))
		$publication=$issueinfo[1].'/'.$issueinfo[2].$issueinfo[3];
	elseif($scanindex->validate_issue_code($issueinfo[1].'/'.$issueinfo[2],'publication'))
		$publication=$issueinfo[1].'/'.$issueinfo[2];
}
}
else
	echo "<p>Add torrent for issue</p>\n";
if(isset($_GET['issue']))
	$publication=$_GET['issue'];
?>

    <form name="form1" method="post" action="addissue_submit.php">
  <p>Issue: 
    <input type="text" name="issuecode" id="issuecode" value="<?php echo $publication; ?>" onKeyUp="validate_issue_code()">
    <span id="validcode"></span>
  </p>
  <p>Torrent site: 
    <input type="text" name="torrentsite" id="torrentsite" list="torrentsites" onChange="get_search_link()" onKeyUp="get_search_link()">
    <a href="" id="induckslink"></a></p>
  <p>Torrent id: 
    <input type="text" name="torrentid" id="torrentid">
	<a href="" id="searchlink"></a>
  </p>
  <p>
    <input type="submit" name="button" id="button" value="Submit">
  </p>
	<input type="hidden" name="file" value="<?Php echo $file; ?>" />
</form>

</body>
</html>