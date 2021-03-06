<?Php
class scanindex
{
	public $db_coa;
	public $db_scanindex;
	public $filepath;
	function __construct()
	{
		require 'config.php';
		$this->filepath=$filepath;
		
		$this->db_coa = new PDO("mysql:host=$coa_db_host;dbname=$coa_db_name",$coa_db_user,$coa_db_pass);
		if($this->db_coa===false)
			trigger_error("Unable to open coa database",E_USER_ERROR);
		$this->db_scanindex = new PDO("mysql:host=$scanindex_db_host;dbname=$scanindex_db_name",$scanindex_db_user,$scanindex_db_pass);
		if($this->db_scanindex===false)
			trigger_error("Unable to open scan index database",E_USER_ERROR);
	}
	function validate_issue_code($code,$mode='issue')
	{
		if($mode=='issue')
			$st_issuecode=$this->db_coa->prepare("SELECT issuecode FROM inducks_issue WHERE issuecode=?");
		elseif($mode=='publication')
			$st_issuecode=$this->db_coa->prepare("SELECT publicationcode FROM inducks_publication WHERE publicationcode=?");
		else
			trigger_error("Invalid mode: $mode",E_USER_ERROR);
		$st_issuecode->execute(array($code));
		if($st_issuecode->rowCount()>0)
			return true;
		else
			return false;
	}
	
}
