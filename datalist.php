<?Php
function datalist($id,$values)
{
	$data="<datalist id=\"$id\">\n";
	foreach ($values as $value)
	{
		$data.="\t<option value=\"{$value}\">\n";
	}
	$data.="</datalist>\n";
	return $data;
}
?>