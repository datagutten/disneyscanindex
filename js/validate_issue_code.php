<?php
require '../class.php';
$scanindex=new scanindex;

if(strlen($_GET['issuecode'])<4)
	die();

$st_issuecode=$scanindex->db_coa->prepare("SELECT issuecode FROM coa.inducks_issue WHERE issuecode=?");
$st_issuecode->execute(array($_GET['issuecode']));
if($st_issuecode->rowCount()>0)
{
	echo "Issue code is valid";
}
else
	echo "Issue code not found";
?>

