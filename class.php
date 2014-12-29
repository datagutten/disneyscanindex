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
	function validate_issue_code($issuecode)
	{
		$st_issuecode=$this->db_coa->prepare("SELECT issuecode FROM coa.inducks_issue WHERE issuecode=?");
		$st_issuecode->execute(array($issuecode));
		if($st_issuecode->rowCount()>0)
			return true;
		else
			return false;
	}
}
