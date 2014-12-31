<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Scan index</title>
</head>

<body>

<?Php
ini_set('display_errors',true);

require 'class.php';
$scanindex=new scanindex;

if(!isset($_GET['person']))
	$personcode='CB';
else
	$personcode=$_GET['person'];
//$personcode='AMi';
$issuecode='no/%';

//Fetch scanned stories
$st_scan=$scanindex->db_scanindex->query("SELECT stories.id AS storyid,stories.storycode,stories.issuecode,files.id AS fileid,files.path FROM stories,files WHERE stories.storycode=files.storycode");
if($st_scan===false)
	print_r($db_scan->errorInfo());

$stories_scan=$st_scan->fetchAll(PDO::FETCH_ASSOC);

$stories_scan_search=array_column($stories_scan,'storycode');

//Fetch all stories by the specified person published in the specified country from coa
$st_coa=$scanindex->db_coa->prepare("SELECT inducks_story.storycode,inducks_story.firstpublicationdate,inducks_entry.title,inducks_entry.issuecode
FROM inducks_storyjob,inducks_storyversion,inducks_story,inducks_entry WHERE inducks_storyjob.personcode=? AND inducks_entry.issuecode LIKE ?
AND (inducks_storyversion.kind='n' OR inducks_storyversion.kind='k')
AND inducks_storyjob.storyversioncode=inducks_storyversion.storyversioncode
AND inducks_storyversion.storycode=inducks_story.storycode
AND inducks_storyjob.storyversioncode=inducks_entry.storyversioncode
ORDER BY inducks_story.firstpublicationdate");
$st_coa->execute(array($personcode,$issuecode));
$stories_coa=$st_coa->fetchAll(PDO::FETCH_ASSOC);
$stories_coa_search=array_column($stories_coa,'storycode');

//Fetch torrent trackers
$st_trackers=$scanindex->db_scanindex->query("SELECT * FROM torrentsites");
$trackers=$st_trackers->fetchAll(PDO::FETCH_ASSOC);

//Fetch torrents
$st_torrents=$scanindex->db_scanindex->prepare("SELECT * FROM torrents WHERE site=?");
foreach($trackers as $tracker)
{
	$st_torrents->execute(array($tracker['name']));
	$torrents[$tracker['name']]=$st_torrents->fetchAll(PDO::FETCH_ASSOC);
	$torrents_search[$tracker['name']]=array_column($torrents[$tracker['name']],'story');
}
//Write table
echo "<table border=\"1\">\n";
foreach(array_unique($stories_coa_search) as $key_coa=>$storycode)
{
	$story_coa=$stories_coa[$key_coa];

	//print_r($stories[$key]);
	echo "<tr>\n";
	echo "\t<td><a href=\"http://coa.inducks.org/story.php?c=".urlencode($story_coa['storycode'])."\">{$story_coa['storycode']}</td>\n";
	echo "\t<td>{$story_coa['title']}</td>\n";
	echo "\t<td>{$story_coa['firstpublicationdate']}</td>\n";
	
	$key_scan=array_search($story_coa['storycode'],$stories_scan_search); //Find scanned stories wity storycode from coa
	if($key_scan!==false)
	{
		$story_scan=$stories_scan[$key_scan];
		echo "\t<td>{$story_scan['path']}</td>\n";
	}
	else
	{
		echo "\t<td colspan=\"3\">&nbsp;</td>\n";
		continue;
	}
	foreach($trackers as $tracker)
	{
		$torrentkey=array_search($story_scan['storyid'],$torrents_search[$tracker['name']]); //Find torrents with story id 
		//var_dump($torrentkey);
		if($torrentkey===false || $torrents[$tracker['name']][$torrentkey]['site']!=$tracker['name'])
			echo "\t<td><a href=\"addissue_web_form.php?issue={$story_scan['issuecode']}\">Add torrent from {$tracker['name']}</td>\n";
		else
			echo "\t<td><a href=\"{$tracker['torrenturl']}{$torrents[$tracker['name']][$torrentkey]['torrentid']}\">{$tracker['name']}</a></td>\n";
	}
	//echo "\t<td>{$story_scan['storyid']}";
	//echo nl2br(print_r($story_scan,true));
	//echo "</td>\n";
	echo "</tr>\n";
}
$db=NULL;
$db_scan=NULL;
?>
</body>
</html>