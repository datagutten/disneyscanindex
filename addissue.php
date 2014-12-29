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

$basepath=$scanindex->filepath;
$st_files=$scanindex->db_scanindex->query("SELECT distinct path FROM files");
$files=$st_files->fetchAll(PDO::FETCH_COLUMN);
if(!isset($_GET['file']))
	$dir=$basepath;
elseif(strpos($_GET['file'],$basepath)===false)
	trigger_error("Invalid directory requested",E_USER_ERROR);
else
	$dir=$_GET['file'];

$basepath=$dir;
//print_r($files);
$parentdir=realpath($dir.'/..');
echo "<a href=\"?file=$parentdir\">[..]</a><br />\n";
foreach(array_diff(scandir($dir),array('.','..')) as $file)
{
	if(array_search($dir.'/'.$file,$files)===false)
	{
		if(is_dir($dir.'/'.$file))
			echo "<a href=\"?file=$dir/$file\">$file</a><br />\n";
		else
			echo "<a href=\"addissue_web_form.php?file=".urlencode($basepath.'/'.$file)."\">$file</a><br />\n";
	}

}

?>
</body>
</html>