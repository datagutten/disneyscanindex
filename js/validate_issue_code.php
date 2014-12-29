<?php
require '../class.php';
$scanindex=new scanindex;

if(strlen($_GET['issuecode'])<4)
	die();

if($scanindex->validate_issue_code($_GET['issuecode']))
{
	echo "Issue code is valid";
}
else
	echo "Issue code not found";
?>

