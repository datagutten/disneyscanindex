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
$file=$_GET['file'];
?>
<script type="text/javascript" src="js/addissue_web_form.js"></script>

<?Php
	echo '<span id="searchstring" style="display:none">'.preg_replace('/(.+?)\(.+/','$1',basename($file))."</span>\n";
	$st_sites=$scanindex->db_scanindex->query("SELECT * FROM torrentsites");
	$sites=$st_sites->fetchAll(PDO::FETCH_ASSOC);
	echo datalist('torrentsites',array_column($sites,'name'));
	echo "<p>Adding <span id=\"file\">{$_GET['file']}</span></p>\n";
	?>

    <form name="form1" method="post" action="addissue_submit.php">
  <p>Issue: 
    <input type="text" name="issuecode" id="issuecode" onKeyUp="validate_issue_code()">
    <span id="validcode"></span>
  </p>
  <p>Torrent site: 
    <input type="text" name="torrentsite" id="torrentsite" list="torrentsites" onChange="get_search_link()">
  </p>
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