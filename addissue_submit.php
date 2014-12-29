<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Add issue</title>
</head>

<body>
<?Php
require 'class.php';
$scanindex=new scanindex;
$st_insert_story=$scanindex->db_scanindex->prepare("INSERT INTO stories (storycode,issuecode) VALUES (?,?)");
$st_insert_file=$scanindex->db_scanindex->prepare("INSERT INTO files (story,path,storycode) VALUES (?,?,?)");

if(isset($_POST['file']))
	$file=$_POST['file'];
elseif(isset($argv[1]))
	$file=$argv[1];
else
	die("No file specified\n");

$file=realpath($file);

if(!file_exists($file))
	trigger_error("File \"$file\" does not exist",E_USER_ERROR);
if(getcwd()===false)
	trigger_error("Unable to find current working dir",E_USER_ERROR);
if($file===false || substr($file,0,1)!=='/')
	trigger_error("Unable to find real file path, working dir is ".getcwd(),E_USER_ERROR);

if(isset($_POST['issuecode']))
	$issue=$_POST['issuecode'];
elseif(isset($argv[2]))
	$issue=$argv[2];
else
	die("Issue code not found\n");

//$issue="no/DD2013B19-20";
//$issue="no/DD2013-19-20";
$st_issue=$scanindex->db_coa->prepare("SELECT * FROM coa.inducks_entry,coa.inducks_storyversion WHERE issuecode=? AND coa.inducks_entry.storyversioncode=coa.inducks_storyversion.storyversioncode ORDER BY position;");
$st_issue->execute(array($issue));
if($st_issue->rowCount()==0)
	die("$issue is not a valid issue code\n");
$stories=$st_issue->fetchAll(PDO::FETCH_ASSOC);

$st_issuecheck=$scanindex->db_scanindex->prepare("SELECT id,storycode FROM stories WHERE issuecode=?");
$st_issuecheck->execute(array($issue));
$stories_indb=$st_issuecheck->fetchAll(PDO::FETCH_KEY_PAIR);

$st_files_indb=$scanindex->db_scanindex->prepare("SELECT files.id,files.story,files.path FROM stories,files WHERE stories.id=files.story AND stories.issuecode=?");
$st_files_indb->execute(array($issue));
$files_indb=$st_files_indb->fetchAll(PDO::FETCH_ASSOC);
$files_indb_storyid=array_column($files_indb,'story'); //Make an array with the same keys as $files_indb but with only storyid as value

$st_update_file=$scanindex->db_scanindex->prepare("UPDATE files SET path=? WHERE id=?");

$st_insert_torrent=$scanindex->db_scanindex->prepare("INSERT INTO torrents (site,torrentid,story) VALUES (?,?,?)");

//print_r($files_indb);
//print_r($files_indb_storyid);
//die();

foreach($stories as $story)
{
	//print_r($story);
	$storyid=array_search($story['storycode'],$stories_indb);
	if(empty($story['storycode']))
		continue;
	if($storyid===false) //Story is not in DB
	{
		echo "Adding {$story['storycode']}<br />\n";
		$st_insert_story->execute(array($story['storycode'],$story['issuecode']));
		$storyid=$scanindex->db_scanindex->lastInsertId();
	}
	else
		echo "Story {$story['storycode']} is already added for $issue<br />\n";
	
	if($storyid!==false) //File is not in DB, insert it
		$st_insert_file->execute(array($storyid,$file,$story['storycode']));
	if(($filekey=array_search($storyid,$files_indb_storyid))!==false && $files_indb[$filekey]['path']!=$file) //File is in db, but path is different. Update it
	{
		echo "Updating path for {$story['storycode']} to $file<br />\n";
		$st_update_file->execute(array($file,$files_indb[$filekey]['id']));
	}
		
	if(!empty($_POST['torrentsite']) && !empty($_POST['torrentid']))
	{
		$st_insert_torrent->execute(array($_POST['torrentsite'],$_POST['torrentid'],$storyid));
	}
	
}

echo "<p><a href=\"addissue.php?file=".dirname($file)."\">Add another</a></p>\n";
?>
</body>
</html>