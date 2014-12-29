<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Scan index</title>
</head>

<body>

<?Php
require 'class.php';
$scanindex=new scanindex;

$st_scanstories=$scanindex->db_scanindex->query("SELECT * FROM stories,files WHERE stories.storycode=files.storycode");

if($st_scanstories===false)
	print_r($db_scan->errorInfo());
$stories_scan=$st_scanstories->fetchAll(PDO::FETCH_ASSOC);
$storycodes_scan=array_column($stories_scan,'storycode');

//print_r($storycodes_scan);

if(!isset($_GET['person']))
	$personcode='CB';
else
	$personcode=$_GET['person'];
//$personcode='AMi';
$issuecode='no/%';
/*$st=$db->prepare("SELECT * FROM inducks_storyjob,inducks_story,inducks_entry WHERE inducks_storyjob.personcode=? AND inducks_entry.issuecode LIKE ? AND (inducks_storyversion.kind='n' OR inducks_storyversion.kind='k')
AND inducks_storyjob.storyversioncode=inducks_story.originalstoryversioncode
AND inducks_storyjob.storyversioncode=inducks_entry.storyversioncode");*/
$st_coa=$scanindex->db_coa->prepare("SELECT inducks_story.storycode,inducks_story.firstpublicationdate,inducks_entry.title
FROM inducks_storyjob,inducks_story,inducks_entry,inducks_storyversion WHERE inducks_storyjob.personcode=? AND inducks_entry.issuecode LIKE ? AND (inducks_storyversion.kind='n' OR inducks_storyversion.kind='k')
AND inducks_storyjob.storyversioncode=inducks_story.originalstoryversioncode
AND inducks_storyjob.storyversioncode=inducks_entry.storyversioncode
AND inducks_storyjob.storyversioncode=inducks_storyversion.storyversioncode
ORDER BY inducks_story.firstpublicationdate");
$st_coa->execute(array($personcode,$issuecode));
$stories=$st_coa->fetchAll(PDO::FETCH_ASSOC);

echo "<table border=\"1\">\n";
foreach(array_unique(array_column($stories,'storycode')) as $key=>$story)
{
	//print_r($stories[$key]);
	echo "<tr>\n";
	echo "\t<td><a href=\"http://coa.inducks.org/story.php?c=".urlencode($stories[$key]['storycode'])."\">{$stories[$key]['storycode']}</td>\n";
	echo "\t<td>{$stories[$key]['title']}</td>\n";
	echo "\t<td>{$stories[$key]['firstpublicationdate']}</td>\n";
	$scankey=array_search($stories[$key]['storycode'],$storycodes_scan);
	if($scankey!==false)
		echo "\t<td>{$stories_scan[$scankey]['path']}</td>\n";
	else
		echo "\t<td>&nbsp;</td>\n";
	echo "</tr>\n";
}
$db=NULL;
$db_scan=NULL;
?>
</body>
</html>